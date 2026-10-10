"""Resolve the reviewed exact-accession Operating Income derivations."""

from __future__ import annotations

from dataclasses import dataclass
from datetime import date
from decimal import Decimal, localcontext
from enum import Enum
import re

from valuation_platform.sec.annual_period import (
    AnnualPeriodResolution,
    ResolvedAnnualPeriod,
)
from valuation_platform.sec.fact_selection import FilingFactObservations
from valuation_platform.sec.filing_xbrl import (
    FilingXBRLContext,
    FilingXBRLFact,
    SECFilingXBRL,
)

from .concepts import FinancialMetric
from .models import (
    AmbiguityReason,
    AmbiguousHistoricalMetric,
    DerivationOperation,
    DerivedHistoricalValue,
    EvidenceSourceKind,
    FilingXBRLEvidence,
    HistoricalMetricResult,
    HistoricalPeriod,
    MissingHistoricalMetric,
    MissingReason,
    NormalizedHistoricalValue,
    OperatingIncomeDerivationPolicyProvenance,
    OperatingIncomeOperandEvidence,
    OperatingIncomeValidationEvidence,
    ReviewedPolicyEvidence,
)


OPERATING_INCOME_DERIVATION_POLICY_ID = "operating_income_component_derivation"
OPERATING_INCOME_DERIVATION_POLICY_VERSION = "1"
_USD_NAMESPACE = "http://www.xbrl.org/2003/iso4217"
_ACCESSION = re.compile(r"^[0-9]{10}-[0-9]{2}-[0-9]{6}$")


class OperatingIncomeDerivationPolicyError(ValueError):
    """Raised when curated policy or filing evidence is structurally invalid."""


class OperatingIncomeOperandState(str, Enum):
    """Whether a reviewed statement row supplies a numeric operand."""

    REQUIRED = "required"
    EXPLICITLY_ABSENT = "explicitly_absent"


@dataclass(frozen=True)
class OperatingIncomeReviewedAlternate:
    """One exact reviewed non-face representation retained as provenance."""

    operand_id: str
    value: Decimal
    decimals: str | None
    reason: str = "REVIEWED_NON_FACE_PRECISION"

    def __post_init__(self) -> None:
        if (
            not self.operand_id
            or not isinstance(self.value, Decimal)
            or not self.value.is_finite()
            or not self.reason
        ):
            raise OperatingIncomeDerivationPolicyError(
                "Reviewed alternate occurrence is invalid"
            )


@dataclass(frozen=True)
class OperatingIncomeOperandDefinition:
    """One exact filing-XBRL fact role in a reviewed equation."""

    ordinal: int
    operand_id: str
    economic_role: str
    namespace: str
    concept: str
    expected_value: Decimal | None
    state: OperatingIncomeOperandState = OperatingIncomeOperandState.REQUIRED
    source_kind: EvidenceSourceKind = EvidenceSourceKind.FILING_XBRL
    unit: str = "USD"
    require_empty_dimensions: bool = True

    def __post_init__(self) -> None:
        if (
            not isinstance(self.ordinal, int)
            or isinstance(self.ordinal, bool)
            or self.ordinal < 1
            or not self.operand_id
            or not self.economic_role
            or not self.namespace
            or not self.concept
            or self.source_kind is not EvidenceSourceKind.FILING_XBRL
            or self.unit != "USD"
            or not self.require_empty_dimensions
            or not isinstance(self.state, OperatingIncomeOperandState)
        ):
            raise OperatingIncomeDerivationPolicyError(
                "Operating Income operand definition is invalid"
            )
        if self.state is OperatingIncomeOperandState.REQUIRED:
            if (
                not isinstance(self.expected_value, Decimal)
                or not self.expected_value.is_finite()
            ):
                raise OperatingIncomeDerivationPolicyError(
                    "Required Operating Income operand needs an exact value"
                )
        elif self.expected_value is not None:
            raise OperatingIncomeDerivationPolicyError(
                "Explicitly absent operand cannot have an expected value"
            )


@dataclass(frozen=True)
class OperatingIncomeSignedTerm:
    """One ordered signed term in an approved sum."""

    ordinal: int
    operand_id: str
    coefficient: Decimal

    def __post_init__(self) -> None:
        if (
            not isinstance(self.ordinal, int)
            or isinstance(self.ordinal, bool)
            or self.ordinal < 1
            or not self.operand_id
            or not isinstance(self.coefficient, Decimal)
            or self.coefficient not in (Decimal("1"), Decimal("-1"))
        ):
            raise OperatingIncomeDerivationPolicyError(
                "Operating Income signed term is invalid"
            )


@dataclass(frozen=True)
class OperatingIncomeValidationDefinition:
    """One exact arithmetic check that gates a registered derivation."""

    validation_id: str
    reported_operand_id: str
    terms: tuple[OperatingIncomeSignedTerm, ...]
    expected_variance: Decimal
    display_scale: Decimal

    def __post_init__(self) -> None:
        if (
            not self.validation_id
            or not self.reported_operand_id
            or not isinstance(self.terms, tuple)
            or not self.terms
            or tuple(item.ordinal for item in self.terms)
            != tuple(range(1, len(self.terms) + 1))
            or len({item.operand_id for item in self.terms}) != len(self.terms)
            or not isinstance(self.expected_variance, Decimal)
            or not self.expected_variance.is_finite()
            or not isinstance(self.display_scale, Decimal)
            or not self.display_scale.is_finite()
            or self.display_scale <= 0
        ):
            raise OperatingIncomeDerivationPolicyError(
                "Operating Income validation definition is invalid"
            )


@dataclass(frozen=True)
class OperatingIncomeDerivationEntry:
    """One exact selected-filing Operating Income equation."""

    company_cik: int
    accession_number: str
    report_date: date
    annual_start: date
    annual_end: date
    formula_id: str
    perimeter_id: str
    expected_value: Decimal
    operands: tuple[OperatingIncomeOperandDefinition, ...]
    calculation_terms: tuple[OperatingIncomeSignedTerm, ...]
    validations: tuple[OperatingIncomeValidationDefinition, ...]
    reviewed_alternates: tuple[OperatingIncomeReviewedAlternate, ...]
    reviewed_evidence: tuple[ReviewedPolicyEvidence, ...]
    unit: str = "USD"
    form: str = "10-K"

    @property
    def key(self) -> tuple[object, ...]:
        return (
            self.company_cik,
            self.accession_number,
            self.report_date,
            self.annual_start,
            self.annual_end,
        )

    def __post_init__(self) -> None:
        if not all(isinstance(items, tuple) for items in (
            self.operands, self.calculation_terms, self.validations,
            self.reviewed_alternates, self.reviewed_evidence,
        )):
            raise OperatingIncomeDerivationPolicyError("Policy containers must be immutable")
        operand_ids = tuple(item.operand_id for item in self.operands)
        calculation_ids = tuple(item.operand_id for item in self.calculation_terms)
        if any(item not in operand_ids for item in calculation_ids):
            raise OperatingIncomeDerivationPolicyError("Unregistered calculation operand")
        calculation_definitions = tuple(
            self.operands[operand_ids.index(item)] for item in calculation_ids
        )
        if (
            not isinstance(self.company_cik, int)
            or isinstance(self.company_cik, bool)
            or self.company_cik < 0
            or _ACCESSION.fullmatch(self.accession_number) is None
            or self.form != "10-K"
            or self.annual_start >= self.annual_end
            or self.annual_end != self.report_date
            or not self.formula_id
            or not self.perimeter_id
            or self.unit != "USD"
            or not isinstance(self.expected_value, Decimal)
            or not self.expected_value.is_finite()
            or not self.operands
            or tuple(item.ordinal for item in self.operands)
            != tuple(range(1, len(self.operands) + 1))
            or len(set(operand_ids)) != len(operand_ids)
            or not self.calculation_terms
            or tuple(item.ordinal for item in self.calculation_terms)
            != tuple(range(1, len(self.calculation_terms) + 1))
            or len(set(calculation_ids)) != len(calculation_ids)
            or len(
                {(item.namespace, item.concept) for item in calculation_definitions}
            )
            != len(calculation_definitions)
            or any(item not in operand_ids for item in calculation_ids)
            or any(
                self.operands[operand_ids.index(item)].state
                is not OperatingIncomeOperandState.REQUIRED
                for item in calculation_ids
            )
            or not self.validations
            or not self.reviewed_evidence
            or any(item.review_status != "approved" for item in self.reviewed_evidence)
        ):
            raise OperatingIncomeDerivationPolicyError(
                "Operating Income derivation entry is invalid"
            )
        for validation in self.validations:
            references = (
                validation.reported_operand_id,
                *(item.operand_id for item in validation.terms),
            )
            if any(item not in operand_ids for item in references):
                raise OperatingIncomeDerivationPolicyError(
                    "Validation references an unregistered operand"
                )
        if any(item.operand_id not in operand_ids for item in self.reviewed_alternates):
            raise OperatingIncomeDerivationPolicyError(
                "Reviewed alternate references an unregistered operand"
            )
        if len({item.evidence_id for item in self.reviewed_evidence}) != len(
            self.reviewed_evidence
        ):
            raise OperatingIncomeDerivationPolicyError(
                "Reviewed evidence IDs must be unique within an entry"
            )


@dataclass(frozen=True)
class OperatingIncomeDerivationPolicy:
    """Immutable exact-accession registry of reviewed equations."""

    policy_id: str
    version: str
    metric: FinancialMetric
    economic_scope: str
    entries: tuple[OperatingIncomeDerivationEntry, ...]

    def __post_init__(self) -> None:
        if not isinstance(self.entries, tuple):
            raise OperatingIncomeDerivationPolicyError("Policy entries must be immutable")
        evidence_ids = tuple(
            item.evidence_id
            for entry in self.entries
            for item in entry.reviewed_evidence
        )
        if (
            self.policy_id != OPERATING_INCOME_DERIVATION_POLICY_ID
            or self.version != OPERATING_INCOME_DERIVATION_POLICY_VERSION
            or self.metric is not FinancialMetric.OPERATING_INCOME
            or not self.economic_scope
            or len(self.entries) != 25
            or len({entry.key for entry in self.entries}) != len(self.entries)
            or len(set(evidence_ids)) != len(evidence_ids)
        ):
            raise OperatingIncomeDerivationPolicyError(
                "Operating Income derivation policy is structurally invalid: "
                f"id={self.policy_id!r}, version={self.version!r}, "
                f"metric={self.metric!r}, scope={self.economic_scope!r}, "
                f"entries={len(self.entries)}, keys={len({entry.key for entry in self.entries})}, "
                f"evidence={len(evidence_ids)}/{len(set(evidence_ids))}"
            )


def _d(value: str | int) -> Decimal:
    return Decimal(str(value))


def _term(ordinal: int, operand_id: str, coefficient: int) -> OperatingIncomeSignedTerm:
    return OperatingIncomeSignedTerm(ordinal, operand_id, _d(coefficient))


def _operand(
    ordinal: int,
    operand_id: str,
    role: str,
    namespace: str,
    concept: str,
    value: int | None,
    *,
    absent: bool = False,
) -> OperatingIncomeOperandDefinition:
    return OperatingIncomeOperandDefinition(
        ordinal,
        operand_id,
        role,
        namespace,
        concept,
        None if value is None else _d(value),
        OperatingIncomeOperandState.EXPLICITLY_ABSENT
        if absent
        else OperatingIncomeOperandState.REQUIRED,
    )


def _validation(
    validation_id: str,
    reported: str,
    terms: tuple[tuple[str, int], ...],
    variance: int = 0,
    scale: int = 1,
) -> OperatingIncomeValidationDefinition:
    return OperatingIncomeValidationDefinition(
        validation_id,
        reported,
        tuple(_term(index, operand_id, coefficient) for index, (operand_id, coefficient) in enumerate(terms, 1)),
        _d(variance),
        _d(scale),
    )


def _evidence(
    ticker: str,
    cik: int,
    accession: str,
    year: int,
    instance_name: str,
    face_name: str,
    calc_name: str,
) -> tuple[ReviewedPolicyEvidence, ...]:
    base = (
        f"https://www.sec.gov/Archives/edgar/data/{cik}/"
        f"{accession.replace('-', '')}"
    )
    common = dict(
        research_artifact="docs/operating-income-derivation-design.md",
        reviewed_on=date(2026, 10, 9),
        review_status="approved",
        rationale=(
            "Exact selected-filing face facts and submitted calculation relationships "
            "establish a complete, nonoverlapping Operating Income equation."
        ),
        content_digest=(
            f"{ticker} {year} reviewed Revenue-to-Operating-Income and "
            "Operating-Income-to-Pretax bridge."
        ),
    )
    locations = (
        ("instance", instance_name, "SEC extracted XBRL instance"),
        ("face", face_name, "Consolidated income/operations statement"),
        ("calculation", calc_name, "Filer-submitted calculation linkbase"),
    )
    if ticker == "IBM" and year == 2025:
        locations += (
            ("segment", "R39.htm", "Reviewed IP/custom-development operating perimeter"),
            ("other", "R16.htm", "Reviewed Other income/expense nonoperating perimeter"),
            ("retirement", "R31.htm", "Reviewed service/non-service pension perimeter"),
        )
    return tuple(
        ReviewedPolicyEvidence(
            evidence_id=(
                f"{ticker.lower()}-{accession.replace('-', '')}-"
                f"operating-income-{kind}"
            ),
            source_url=f"{base}/{name}",
            filing_location=location,
            **common,
        )
        for kind, name, location in locations
    )


def _entry(
    ticker: str,
    cik: int,
    accession: str,
    start: date,
    end: date,
    formula_id: str,
    expected_value: int,
    operands: tuple[OperatingIncomeOperandDefinition, ...],
    calculation: tuple[tuple[str, int], ...],
    validations: tuple[OperatingIncomeValidationDefinition, ...],
    primary_stem: str,
    face_name: str,
    *,
    calc_stem: str | None = None,
    alternates: tuple[OperatingIncomeReviewedAlternate, ...] = (),
) -> OperatingIncomeDerivationEntry:
    return OperatingIncomeDerivationEntry(
        company_cik=cik,
        accession_number=accession,
        report_date=end,
        annual_start=start,
        annual_end=end,
        formula_id=formula_id,
        perimeter_id=formula_id,
        expected_value=_d(expected_value),
        operands=operands,
        calculation_terms=tuple(
            _term(index, operand_id, coefficient)
            for index, (operand_id, coefficient) in enumerate(calculation, 1)
        ),
        validations=validations,
        reviewed_alternates=alternates,
        reviewed_evidence=_evidence(
            ticker,
            cik,
            accession,
            end.year,
            f"{primary_stem}_htm.xml",
            face_name,
            f"{calc_stem or primary_stem}_cal.xml",
        ),
    )


def _us_gaap(year: str) -> str:
    return f"http://fasb.org/us-gaap/{year}"


def _lly_entries() -> tuple[OperatingIncomeDerivationEntry, ...]:
    rows = (
        ("0000059478-22-000068", date(2021,1,1), date(2021,12,31), "2021-01-31", "http://www.lilly.com/20211231", "AcquiredInProcessResearchAndDevelopment", 28318400000,7312800000,7025900000,6431600000,874900000,316100000,-201600000,6155500000,6357100000,"-5",None),
        ("0000059478-23-000082", date(2022,1,1), date(2022,12,31), "2022", "http://www.lilly.com/20221231", "AcquiredInProcessResearchAndDevelopmentAndDevelopmentMilestones", 28541400000,6629800000,7190800000,6440400000,908500000,244600000,-320900000,6806400000,7127300000,"-5",None),
        ("0000059478-24-000065", date(2023,1,1), date(2023,12,31), "2023", None, "ResearchAndDevelopmentAssetAcquiredOtherThanThroughBusinessCombinationWrittenOff",34124100000,7082200000,9313400000,7403100000,3799800000,67700000,96700000,6554600000,6457900000,"-5",(3800000000,"-7")),
        ("0000059478-25-000067", date(2024,1,1), date(2024,12,31), "2024", None, "ResearchAndDevelopmentAssetAcquiredOtherThanThroughBusinessCombinationWrittenOff",45042700000,8418300000,10990600000,8593800000,3280400000,860600000,-218600000,12680400000,12899000000,"-5",(3280000000,"-7")),
        ("0000059478-26-000013", date(2025,1,1), date(2025,12,31), "2025", None, "ResearchAndDevelopmentAssetAcquiredOtherThanThroughBusinessCombinationWrittenOff",65179000000,11052000000,13337000000,11094000000,2910000000,484000000,-571000000,25731000000,26302000000,"-6",(2900000000,"-8")),
    )
    entries = []
    for acc,start,end,tax,issuer_ns,a_concept,r,c,d,s,a,x,n,t,oi,_,alternate in rows:
        ns=_us_gaap(tax)
        operands=(
            _operand(1,"R","Revenue",ns,"Revenues",r),
            _operand(2,"C","Cost of sales",ns,"CostOfGoodsAndServicesSold",c),
            _operand(3,"D","Research and development",ns,"ResearchAndDevelopmentExpense" if end.year<2023 else "ResearchAndDevelopmentExpenseExcludingAcquiredInProcessCost",d),
            _operand(4,"S","Selling, general and administrative",ns,"SellingGeneralAndAdministrativeExpense",s),
            _operand(5,"A","Acquired IPR&D",issuer_ns or ns,a_concept,a),
            _operand(6,"X","Restructuring and impairment",ns,"RestructuringSettlementAndImpairmentProvisions",x),
            _operand(7,"N","Other net income or expense",ns,"NonoperatingIncomeExpense",n),
            _operand(8,"T","Reported Pretax Income",ns,"IncomeLossFromContinuingOperationsBeforeIncomeTaxesExtraordinaryItemsNoncontrollingInterest",t),
        )
        alternates=() if alternate is None else (OperatingIncomeReviewedAlternate("A",_d(alternate[0]),alternate[1]),)
        stem=f"lly-{end:%Y%m%d}"
        entries.append(_entry("LLY",59478,acc,start,end,"LLY_OPERATING_PERIMETER_V1",oi,operands,(("R",1),("C",-1),("D",-1),("S",-1),("A",-1),("X",-1)),(_validation("pretax_bridge","T",(("R",1),("C",-1),("D",-1),("S",-1),("A",-1),("X",-1),("N",1))),),stem,"R3.htm",alternates=alternates))
    return tuple(entries)


def _jnj_entries() -> tuple[OperatingIncomeDerivationEntry, ...]:
    rows=(
        ("0000200406-22-000022",date(2021,1,4),date(2022,1,2),"2021-01-31",None,"ResearchAndDevelopmentInProcess","InterestExpense",93775000000,29855000000,63920000000,24659000000,14714000000,900000000,252000000,53000000,183000000,-489000000,22776000000,23395000000),
        ("0000200406-23-000016",date(2022,1,3),date(2023,1,1),"2022",None,"ResearchAndDevelopmentInProcess","InterestExpense",94943000000,31089000000,63854000000,24765000000,14603000000,783000000,321000000,490000000,276000000,-1871000000,21725000000,23382000000),
        ("0000200406-24-000013",date(2023,1,2),date(2023,12,31),"2023","http://www.jnj.com/20231231","ResearchAndDevelopmentInProcess1","InterestExpense",85159000000,26553000000,58606000000,21512000000,15085000000,313000000,489000000,1261000000,772000000,-6634000000,15062000000,21207000000),
        ("0000200406-25-000038",date(2024,1,1),date(2024,12,29),"2024","http://www.jnj.com/20241229","ResearchAndDevelopmentInProcess1","InterestExpenseNonoperating",88821000000,27471000000,61350000000,22869000000,17232000000,211000000,234000000,1332000000,755000000,-4694000000,16687000000,20804000000),
        ("0000200406-26-000016",date(2024,12,30),date(2025,12,28),"2025","http://www.jnj.com/20251228","ResearchAndDevelopmentInProcess1","InterestExpenseNonoperating",94193000000,30256000000,63937000000,23676000000,14665000000,81000000,228000000,1056000000,971000000,7209000000,32581000000,25287000000),
    )
    result=[]
    for acc,start,end,tax,issuer_ns,a_concept,e_concept,r,c,g,s,d,a,x,h,e,n,t,oi in rows:
        ns=_us_gaap(tax)
        operands=(
            _operand(1,"R","Revenue",ns,"RevenueFromContractWithCustomerExcludingAssessedTax",r),_operand(2,"C","Cost of products sold",ns,"CostOfGoodsAndServicesSold",c),_operand(3,"G","Gross profit",ns,"GrossProfit",g),_operand(4,"S","Selling, general and administrative",ns,"SellingGeneralAndAdministrativeExpense",s),_operand(5,"D","Research and development",ns,"ResearchAndDevelopmentExpenseExcludingAcquiredInProcessCost",d),_operand(6,"A","In-process R&D",issuer_ns or ns,a_concept,a),_operand(7,"X","Restructuring",ns,"RestructuringCharges",x),_operand(8,"H","Interest income",ns,"InvestmentIncomeInterest",h),_operand(9,"E","Interest expense",ns,e_concept,e),_operand(10,"N","Other nonoperating income or expense",ns,"OtherNonoperatingIncomeExpense",n),_operand(11,"T","Reported Pretax Income",ns,"IncomeLossFromContinuingOperationsBeforeIncomeTaxesExtraordinaryItemsNoncontrollingInterest",t),
        )
        stem=f"jnj-{end:%Y%m%d}"
        result.append(_entry("JNJ",200406,acc,start,end,"JNJ_OPERATING_PERIMETER_V1",oi,operands,(("G",1),("S",-1),("D",-1),("A",-1),("X",-1)),(_validation("gross_profit","G",(("R",1),("C",-1))),_validation("pretax_bridge","T",(("G",1),("S",-1),("D",-1),("A",-1),("X",-1),("H",1),("E",-1),("N",1)))),stem,"R5.htm"))
    return tuple(result)


def _mrk_entries() -> tuple[OperatingIncomeDerivationEntry, ...]:
    rows=(
        ("0000310158-22-000003",2021,48704000000,13626000000,9634000000,12245000000,661000000,1341000000,13879000000,12538000000,"2021-01-31"),
        ("0001628280-23-005061",2022,59283000000,17411000000,10042000000,13548000000,337000000,-1501000000,16444000000,17945000000,"2022"),
        ("0001628280-24-006850",2023,60115000000,16126000000,10504000000,30531000000,599000000,-466000000,1889000000,2355000000,"2023"),
        ("0001628280-25-007732",2024,64168000000,15193000000,10816000000,17938000000,309000000,24000000,19936000000,19912000000,"2024"),
        ("0000310158-26-000063",2025,65011000000,16382000000,10733000000,15789000000,889000000,-151000000,21067000000,21218000000,"2025"),
    )
    result=[]
    for acc,year,r,c,s,d,x,n,t,oi,tax in rows:
        start,end=date(year,1,1),date(year,12,31); ns=_us_gaap(tax)
        operands=(_operand(1,"R","Revenue",ns,"Revenues",r),_operand(2,"C","Cost of sales",ns,"CostOfGoodsAndServicesSold",c),_operand(3,"S","Selling, general and administrative",ns,"SellingGeneralAndAdministrativeExpense",s),_operand(4,"D","Research and development",ns,"ResearchAndDevelopmentExpense",d),_operand(5,"X","Restructuring",ns,"RestructuringCharges",x),_operand(6,"N","Other nonoperating income or expense",ns,"OtherNonoperatingIncomeExpense",n),_operand(7,"T","Reported Pretax Income",ns,"IncomeLossFromContinuingOperationsBeforeIncomeTaxesExtraordinaryItemsNoncontrollingInterest",t))
        stem=f"mrk-{year}1231"
        result.append(_entry("MRK",310158,acc,start,end,"MRK_OPERATING_PERIMETER_V1",oi,operands,(("R",1),("C",-1),("S",-1),("D",-1),("X",-1)),(_validation("pretax_bridge","T",(("R",1),("C",-1),("S",-1),("D",-1),("X",-1),("N",1))),),stem,"R3.htm"))
    return tuple(result)


def _klac_entries() -> tuple[OperatingIncomeDerivationEntry, ...]:
    rows=(
        ("0000319201-22-000023",date(2021,7,1),date(2022,6,30),"2022",9211883000,3592441000,1105254000,860007000,"GoodwillImpairmentLoss",0,False,"InterestExpense",160339000,0,False,-4605000,3489237000,3654181000),
        ("0000319201-23-000031",date(2022,7,1),date(2023,6,30),"2023",10496056000,4218307000,1296727000,986326000,"GoodwillImpairmentLoss",None,True,"InterestExpense",296940000,-13286000,False,104720000,3789190000,3994696000),
        ("0000319201-24-000021",date(2023,7,1),date(2024,6,30),"2024",9812247000,3928073000,1278981000,969509000,"AssetImpairmentCharges",289474000,False,"InterestExpenseNonoperating",311253000,0,False,155075000,3190032000,3346210000),
        ("0000319201-25-000024",date(2024,7,1),date(2025,6,30),"2025",12156162000,4751867000,1360334000,1029734000,"AssetImpairmentCharges",239100000,False,"InterestExpenseNonoperating",302166000,0,False,171487000,4644448000,4775127000),
        ("0000319201-26-000027",date(2025,7,1),date(2026,6,30),"2026",13579476000,5255060000,1532118000,1131518000,"AssetImpairmentCharges",0,False,"InterestExpenseNonoperating",284440000,None,True,229585000,5605925000,5660780000),
    )
    result=[]
    for acc,start,end,tax,r,c,d,s,i_concept,i,i_abs,e_concept,e,l,l_abs,n,t,oi in rows:
        ns=_us_gaap(tax)
        operands=(_operand(1,"R","Revenue",ns,"RevenueFromContractWithCustomerExcludingAssessedTax",r),_operand(2,"C","Cost of revenue",ns,"CostOfRevenue",c),_operand(3,"D","Research and development",ns,"ResearchAndDevelopmentExpense",d),_operand(4,"S","Selling, general and administrative",ns,"SellingGeneralAndAdministrativeExpense",s),_operand(5,"I","Operating impairment",ns,i_concept,i,absent=i_abs),_operand(6,"E","Interest expense",ns,e_concept,e),_operand(7,"L","Debt extinguishment gain or loss",ns,"GainsLossesOnExtinguishmentOfDebt",l,absent=l_abs),_operand(8,"N","Other nonoperating income or expense",ns,"OtherNonoperatingIncomeExpense",n),_operand(9,"T","Reported Pretax Income",ns,"IncomeLossFromContinuingOperationsBeforeIncomeTaxesExtraordinaryItemsNoncontrollingInterest",t))
        calc=(("R",1),("C",-1),("D",-1),("S",-1))+(() if i_abs else (("I",-1),))
        bridge=calc+(("E",-1),)+(() if l_abs else (("L",1),))+(("N",1),)
        alternates=(OperatingIncomeReviewedAlternate("I",_d(0),"-3","REVIEWED_NON_FACE_ABSENCE"),) if end.year==2023 else ()
        stem=f"klac-{end:%Y%m%d}"
        result.append(_entry("KLAC",319201,acc,start,end,"KLAC_OPERATING_PERIMETER_V1",oi,operands,calc,(_validation("pretax_bridge","T",bridge),),stem,"R5.htm",alternates=alternates))
    return tuple(result)


def _ibm_entries() -> tuple[OperatingIncomeDerivationEntry, ...]:
    rows=(
        ("0001558370-22-001584",2021,"2021-01-31",57350000000,25865000000,31486000000,18745000000,6488000000,612000000,"OtherIncomeAndExpense",873000000,1155000000,4837000000,6865000000,-1000000,0,"ibm-20211231x10k","ibm-20211231","R2.htm"),
        ("0001558370-23-002376",2022,"2022",60530000000,27842000000,32687000000,18609000000,6567000000,663000000,"OtherIncomeAndExpense",5803000000,1216000000,1156000000,8174000000,1000000,-1000000,"ibm-20221231x10k","ibm-20221231","R2.htm"),
        ("0000051143-24-000012",2023,"2023",61860000000,27560000000,34300000000,19003000000,6775000000,860000000,"OtherIncomeAndExpense",-914000000,1607000000,8690000000,9382000000,0,-1000000,"ibm-20231231",None,"R3.htm"),
        ("0000051143-25-000015",2024,"2024",62753000000,27201000000,35551000000,19688000000,7479000000,996000000,"OtherExpenseAndIncome",1871000000,1712000000,5797000000,9380000000,1000000,0,"ibm-20241231",None,"R3.htm"),
        ("0000051143-26-000010",2025,"2025",67535000000,28239000000,39297000000,20123000000,8316000000,964000000,"OtherExpenseAndIncome",-442000000,1935000000,10328000000,11822000000,-1000000,1000000,"ibm-20251231",None,"R3.htm"),
    )
    result=[]
    for acc,year,tax,r,c,g,s,d,a,n_concept,n,e,t,oi,gvar,tvar,stem,calc_stem,face in rows:
        start,end=date(year,1,1),date(year,12,31); ns=_us_gaap(tax); ins=f"http://www.ibm.com/{year}1231"
        operands=(_operand(1,"R","Revenue",ns,"Revenues",r),_operand(2,"C","Cost",ns,"CostOfRevenue",c),_operand(3,"G","Gross profit",ns,"GrossProfit",g),_operand(4,"S","Selling, general and administrative",ns,"SellingGeneralAndAdministrativeExpense",s),_operand(5,"D","Research and development",ns,"ResearchAndDevelopmentExpense",d),_operand(6,"A","IP and custom development income",ins,"IntellectualPropertyAndCustomDevelopmentIncome",a),_operand(7,"N","Other income and expense",ins,n_concept,n),_operand(8,"E","Interest expense",ns,"InterestExpense",e),_operand(9,"T","Reported Pretax Income",ns,"IncomeLossFromContinuingOperationsBeforeIncomeTaxesExtraordinaryItemsNoncontrollingInterest",t))
        result.append(_entry("IBM",51143,acc,start,end,"IBM_OPERATING_PERIMETER_V1",oi,operands,(("G",1),("S",-1),("D",-1),("A",1)),(_validation("gross_profit","G",(("R",1),("C",-1)),gvar,1000000),_validation("pretax_bridge","T",(("G",1),("S",-1),("D",-1),("A",1),("N",-1),("E",-1)),tvar,1000000)),stem,face,calc_stem=calc_stem))
    return tuple(result)


OPERATING_INCOME_COMPONENT_DERIVATION_POLICY = OperatingIncomeDerivationPolicy(
    policy_id=OPERATING_INCOME_DERIVATION_POLICY_ID,
    version=OPERATING_INCOME_DERIVATION_POLICY_VERSION,
    metric=FinancialMetric.OPERATING_INCOME,
    economic_scope="consolidated_continuing_operations_operating_income",
    entries=(*_lly_entries(), *_jnj_entries(), *_mrk_entries(), *_klac_entries(), *_ibm_entries()),
)

if len(OPERATING_INCOME_COMPONENT_DERIVATION_POLICY.entries) != 25:
    raise OperatingIncomeDerivationPolicyError(
        "Operating Income v1 registry must contain exactly 25 entries"
    )


@dataclass(frozen=True)
class _Occurrence:
    source_index: int
    fact: FilingXBRLFact
    context: FilingXBRLContext


def operating_income_derivation_entry_for(
    company_cik: int,
    accession_number: str,
    report_date: date,
    annual_start: date,
    annual_end: date,
    policy: OperatingIncomeDerivationPolicy = OPERATING_INCOME_COMPONENT_DERIVATION_POLICY,
) -> OperatingIncomeDerivationEntry | None:
    """Return only an exact active-policy entry."""
    key = (company_cik, accession_number, report_date, annual_start, annual_end)
    return next((entry for entry in policy.entries if entry.key == key), None)


def apply_curated_operating_income_derivation_policy(
    bucket: FilingFactObservations,
    direct_result: HistoricalMetricResult,
    company_cik: int,
    annual_period: AnnualPeriodResolution | None,
    filing_xbrl: SECFilingXBRL | None,
    policy: OperatingIncomeDerivationPolicy = OPERATING_INCOME_COMPONENT_DERIVATION_POLICY,
) -> HistoricalMetricResult:
    """Apply the exact reviewed derivation after unchanged direct resolution."""
    if direct_result.metric is not FinancialMetric.OPERATING_INCOME:
        raise OperatingIncomeDerivationPolicyError(
            "Operating Income derivation received another metric"
        )
    if isinstance(direct_result, AmbiguousHistoricalMetric):
        return direct_result
    filing = bucket.filing
    if (
        filing.form != "10-K"
        or filing.report_date is None
        or not isinstance(annual_period, ResolvedAnnualPeriod)
    ):
        return direct_result
    entry = operating_income_derivation_entry_for(
        company_cik,
        filing.accession_number,
        filing.report_date,
        annual_period.start,
        annual_period.end,
        policy,
    )
    if entry is None:
        return direct_result
    if filing_xbrl is None:
        return direct_result if isinstance(direct_result, NormalizedHistoricalValue) else _missing(entry)
    if (
        filing_xbrl.company.cik != company_cik
        or filing_xbrl.filing != filing
        or filing_xbrl.filing.accession_number != entry.accession_number
    ):
        raise OperatingIncomeDerivationPolicyError(
            "Operating Income filing-XBRL identity is inconsistent"
        )

    evidence_by_id: dict[str, OperatingIncomeOperandEvidence] = {}
    ambiguous_candidates: list[FilingXBRLEvidence] = []
    incomplete = False
    for definition in entry.operands:
        resolved, conflicts = _resolve_operand(entry, definition, filing_xbrl)
        if conflicts:
            ambiguous_candidates.extend(conflicts)
        elif resolved is None:
            incomplete = True
        else:
            evidence_by_id[definition.operand_id] = resolved
    if ambiguous_candidates:
        if isinstance(direct_result, NormalizedHistoricalValue):
            candidates = (
                direct_result.chosen_source,
                *direct_result.confirming_sources,
                *ambiguous_candidates,
            )
        else:
            candidates = tuple(ambiguous_candidates)
        return AmbiguousHistoricalMetric(
            FinancialMetric.OPERATING_INCOME,
            AmbiguityReason.CONFLICTING_CONCEPT_VALUES,
            candidates,
        )
    if incomplete:
        return direct_result if isinstance(direct_result, NormalizedHistoricalValue) else _missing(entry)

    with localcontext() as context:
        context.prec = 34
        calculated = sum(
            (
                term.coefficient
                * _required_value(evidence_by_id[term.operand_id])
                for term in entry.calculation_terms
            ),
            Decimal("0"),
        )
    if calculated != entry.expected_value:
        raise OperatingIncomeDerivationPolicyError(
            "Operating Income registry arithmetic does not match reviewed value"
        )

    coefficients = {item.operand_id: item.coefficient for item in entry.calculation_terms}
    ordered_evidence = tuple(
        OperatingIncomeOperandEvidence(
            ordinal=index,
            operand_id=item.operand_id,
            economic_role=item.economic_role,
            namespace=item.namespace,
            concept=item.concept,
            expected_value=item.expected_value,
            coefficient=coefficients.get(item.operand_id),
            contribution=(
                None
                if item.operand_id not in coefficients
                else coefficients[item.operand_id] * _required_value(evidence_by_id[item.operand_id])
            ),
            occurrences=evidence_by_id[item.operand_id].occurrences,
            reviewed_nonselected_occurrences=evidence_by_id[item.operand_id].reviewed_nonselected_occurrences,
            absence_reviewed=evidence_by_id[item.operand_id].absence_reviewed,
            reviewed_nonselected_reasons=evidence_by_id[item.operand_id].reviewed_nonselected_reasons,
        )
        for index, item in enumerate(entry.operands, 1)
    )
    validations = tuple(
        _evaluate_validation(validation, evidence_by_id)
        for validation in entry.validations
    )
    if not all(item.passed for item in validations):
        return direct_result if isinstance(direct_result, NormalizedHistoricalValue) else _missing(entry)
    provenance = OperatingIncomeDerivationPolicyProvenance(
        policy_id=policy.policy_id,
        policy_version=policy.version,
        company_cik=entry.company_cik,
        accession_number=entry.accession_number,
        report_date=entry.report_date,
        annual_start=entry.annual_start,
        annual_end=entry.annual_end,
        formula_id=entry.formula_id,
        perimeter_id=entry.perimeter_id,
        unit=entry.unit,
        calculated_value=calculated,
        reviewed_evidence=entry.reviewed_evidence,
        operands=ordered_evidence,
        validations=validations,
    )
    calculation_sources = tuple(
        evidence_by_id[term.operand_id].occurrences[0]
        for term in entry.calculation_terms
    )
    derived = DerivedHistoricalValue(
        metric=FinancialMetric.OPERATING_INCOME,
        value=calculated,
        unit="USD",
        period=HistoricalPeriod(entry.annual_start, entry.annual_end),
        policy_id=policy.policy_id,
        operation=DerivationOperation.ADD,
        operands=calculation_sources,
        policy_version=policy.version,
        derivation_provenance=provenance,
    )
    if isinstance(direct_result, NormalizedHistoricalValue):
        if Decimal(str(direct_result.value)) != calculated or direct_result.period != derived.period:
            return AmbiguousHistoricalMetric(
                FinancialMetric.OPERATING_INCOME,
                AmbiguityReason.CONFLICTING_CONCEPT_VALUES,
                (
                    direct_result.chosen_source,
                    *direct_result.confirming_sources,
                    *calculation_sources,
                ),
                (provenance,),
            )
        return NormalizedHistoricalValue(
            metric=direct_result.metric,
            value=direct_result.value,
            unit=direct_result.unit,
            period=direct_result.period,
            chosen_source=direct_result.chosen_source,
            confirming_sources=direct_result.confirming_sources,
            policy_provenance=direct_result.policy_provenance,
            supporting_derivation_policies=(
                *direct_result.supporting_derivation_policies,
                provenance,
            ),
        )
    if not isinstance(direct_result, MissingHistoricalMetric):
        raise OperatingIncomeDerivationPolicyError(
            "Operating Income direct result has an unsupported type"
        )
    return derived


def _missing(entry: OperatingIncomeDerivationEntry) -> MissingHistoricalMetric:
    from .concepts import ConceptKey

    return MissingHistoricalMetric(
        FinancialMetric.OPERATING_INCOME,
        MissingReason.NO_VALID_DERIVATION_OPERANDS,
        tuple(
            ConceptKey(
                "us-gaap" if item.namespace.startswith("http://fasb.org/us-gaap/") else item.namespace,
                item.concept,
            )
            for item in entry.operands
        ),
    )


def validate_operating_income_derivation_provenance(
    provenance: OperatingIncomeDerivationPolicyProvenance,
) -> None:
    """Reject stripped, forged, or incomplete active-policy provenance."""
    entry = operating_income_derivation_entry_for(
        provenance.company_cik, provenance.accession_number, provenance.report_date,
        provenance.annual_start, provenance.annual_end,
    )
    if (
        entry is None
        or provenance.policy_id != OPERATING_INCOME_DERIVATION_POLICY_ID
        or provenance.policy_version != OPERATING_INCOME_DERIVATION_POLICY_VERSION
        or provenance.formula_id != entry.formula_id
        or provenance.perimeter_id != entry.perimeter_id
        or provenance.unit != entry.unit
        or provenance.calculated_value != entry.expected_value
        or provenance.reviewed_evidence != entry.reviewed_evidence
        or len(provenance.operands) != len(entry.operands)
    ):
        raise OperatingIncomeDerivationPolicyError("Incomplete active derivation provenance")
    coefficients = {term.operand_id: term.coefficient for term in entry.calculation_terms}
    for definition, operand in zip(entry.operands, provenance.operands):
        coefficient = coefficients.get(definition.operand_id)
        if (
            operand.ordinal != definition.ordinal
            or operand.operand_id != definition.operand_id
            or operand.economic_role != definition.economic_role
            or operand.namespace != definition.namespace
            or operand.concept != definition.concept
            or operand.expected_value != definition.expected_value
            or operand.coefficient != coefficient
            or operand.absence_reviewed != (definition.state is OperatingIncomeOperandState.EXPLICITLY_ABSENT)
            or operand.contribution != (None if coefficient is None else coefficient * definition.expected_value)
        ):
            raise OperatingIncomeDerivationPolicyError("Operand definition does not match active entry")
        for evidence in (*operand.occurrences, *operand.reviewed_nonselected_occurrences):
            if (
                evidence.namespace != definition.namespace
                or evidence.concept != definition.concept
                or evidence.accession_number != entry.accession_number
                or evidence.start != entry.annual_start or evidence.end != entry.annual_end
                or evidence.unit != "USD" or evidence.dimensions or evidence.is_nil
                or evidence.entity_identifier_scheme != "http://www.sec.gov/CIK"
                or not evidence.entity_identifier or not evidence.entity_identifier.isdigit()
                or int(evidence.entity_identifier) != entry.company_cik
                or not evidence.context_id or not evidence.unit_ref
                or (entry.company_cik == 51143 and evidence.decimals != "-6")
                or evidence.source_kind is not EvidenceSourceKind.FILING_XBRL
            ):
                raise OperatingIncomeDerivationPolicyError("Operand occurrence identity is incompatible")
        if any(evidence.value != definition.expected_value for evidence in operand.occurrences):
            raise OperatingIncomeDerivationPolicyError("Confirming value is incompatible")
        for evidence, reason in zip(operand.reviewed_nonselected_occurrences, operand.reviewed_nonselected_reasons):
            if not any(alternate.operand_id == definition.operand_id
                       and alternate.value == evidence.value and alternate.decimals == evidence.decimals
                       and alternate.reason == reason for alternate in entry.reviewed_alternates):
                raise OperatingIncomeDerivationPolicyError("Unregistered nonselected occurrence")
    expected_validations = tuple(
        _evaluate_validation(item, {operand.operand_id: operand for operand in provenance.operands})
        for item in entry.validations
    )
    if provenance.validations != expected_validations:
        raise OperatingIncomeDerivationPolicyError("Validation provenance does not match active entry")


def _resolve_operand(
    entry: OperatingIncomeDerivationEntry,
    definition: OperatingIncomeOperandDefinition,
    filing_xbrl: SECFilingXBRL,
) -> tuple[OperatingIncomeOperandEvidence | None, tuple[FilingXBRLEvidence, ...]]:
    contexts = {item.context_id: item for item in filing_xbrl.contexts}
    units = {item.unit_id: item for item in filing_xbrl.units}
    if len(contexts) != len(filing_xbrl.contexts):
        raise OperatingIncomeDerivationPolicyError("Filing contexts are not unique")
    if len(units) != len(filing_xbrl.units):
        raise OperatingIncomeDerivationPolicyError("Filing units are not unique")
    occurrences: list[_Occurrence] = []
    for index, fact in enumerate(filing_xbrl.facts):
        if (
            fact.namespace != definition.namespace
            or fact.concept != definition.concept
            or fact.start != entry.annual_start
            or fact.end != entry.annual_end
        ):
            continue
        context = contexts.get(fact.context_id)
        if context is None:
            raise OperatingIncomeDerivationPolicyError(
                "Operating Income fact references a missing context"
            )
        if (
            fact.start != context.start
            or fact.end != context.end
            or fact.dimensions != context.dimensions
            or fact.accession_number != entry.accession_number
            or fact.source_url != filing_xbrl.source_url
            or (fact.unit is not None and fact.unit_ref != fact.unit.unit_id)
            or (fact.unit is not None and units.get(fact.unit_ref) != fact.unit)
        ):
            raise OperatingIncomeDerivationPolicyError(
                "Operating Income fact linkage is inconsistent"
            )
        if _context_cik(context) != entry.company_cik:
            raise OperatingIncomeDerivationPolicyError(
                "Operating Income fact entity is inconsistent"
            )
        if fact.is_nil and fact.numeric_value is not None:
            raise OperatingIncomeDerivationPolicyError("Nil occurrence contains numeric content")
        if not fact.is_nil and fact.raw_value and fact.numeric_value is None:
            raise OperatingIncomeDerivationPolicyError("Malformed numeric operand")
        if not fact.is_nil and fact.numeric_value is not None:
            try:
                raw_numeric = Decimal(fact.raw_value)
            except (TypeError, ValueError, ArithmeticError) as exc:
                raise OperatingIncomeDerivationPolicyError("Malformed numeric representation") from exc
            if not raw_numeric.is_finite() or raw_numeric != fact.numeric_value:
                raise OperatingIncomeDerivationPolicyError("Raw and numeric values disagree")
            if fact.unit is None or fact.unit_ref not in units:
                raise OperatingIncomeDerivationPolicyError("Numeric operand has a broken unit link")
        occurrences.append(_Occurrence(index, fact, context))

    nondimensional = tuple(item for item in occurrences if not item.fact.dimensions)
    if any(item.fact.is_nil for item in nondimensional) and any(
        isinstance(item.fact.numeric_value, Decimal) and not item.fact.is_nil
        for item in nondimensional
    ):
        raise OperatingIncomeDerivationPolicyError(
            "Operating Income operand has a nil/numeric collision"
        )
    numeric = tuple(
        item
        for item in nondimensional
        if not item.fact.is_nil
        and isinstance(item.fact.numeric_value, Decimal)
        and item.fact.numeric_value.is_finite()
    )
    if numeric and any(_normalized_unit(item.fact) != "USD" for item in numeric):
        return None, ()
    if entry.company_cik == 51143 and any(item.fact.decimals != "-6" for item in numeric):
        return None, ()

    alternates = tuple(
        item
        for item in numeric
        if any(
            alternate.operand_id == definition.operand_id
            and item.fact.numeric_value == alternate.value
            and item.fact.decimals == alternate.decimals
            for alternate in entry.reviewed_alternates
        )
    )
    unregistered = tuple(
        item
        for item in numeric
        if item.fact.numeric_value != definition.expected_value and item not in alternates
    )
    if unregistered:
        return None, tuple(
            _filing_evidence(item, filing_xbrl, ordinal)
            for ordinal, item in enumerate(numeric, 1)
        )
    expected = tuple(
        sorted(
            (item for item in numeric if item.fact.numeric_value == definition.expected_value),
            key=lambda item: item.source_index,
        )
    )
    alternate_evidence = tuple(
        _filing_evidence(item, filing_xbrl, ordinal)
        for ordinal, item in enumerate(sorted(alternates, key=lambda item: item.source_index), 1)
    )
    alternate_reasons = tuple(
        next(alternate.reason for alternate in entry.reviewed_alternates
             if alternate.operand_id == definition.operand_id
             and alternate.value == item.value and alternate.decimals == item.decimals)
        for item in alternate_evidence
    )
    if definition.state is OperatingIncomeOperandState.EXPLICITLY_ABSENT:
        if expected:
            return None, tuple(
                _filing_evidence(item, filing_xbrl, ordinal)
                for ordinal, item in enumerate(expected, 1)
            )
        return (
            OperatingIncomeOperandEvidence(
                definition.ordinal,
                definition.operand_id,
                definition.economic_role,
                definition.namespace,
                definition.concept,
                None,
                None,
                None,
                (),
                alternate_evidence,
                True,
                alternate_reasons,
            ),
            (),
        )
    if not expected:
        return None, ()
    evidence = tuple(
        _filing_evidence(item, filing_xbrl, ordinal)
        for ordinal, item in enumerate(expected, 1)
    )
    return (
        OperatingIncomeOperandEvidence(
            definition.ordinal,
            definition.operand_id,
            definition.economic_role,
            definition.namespace,
            definition.concept,
            definition.expected_value,
            None,
            None,
            evidence,
            alternate_evidence,
            reviewed_nonselected_reasons=alternate_reasons,
        ),
        (),
    )


def _evaluate_validation(
    definition: OperatingIncomeValidationDefinition,
    evidence: dict[str, OperatingIncomeOperandEvidence],
) -> OperatingIncomeValidationEvidence:
    with localcontext() as context:
        context.prec = 34
        calculated = sum(
            (
                term.coefficient * _required_value(evidence[term.operand_id])
                for term in definition.terms
            ),
            Decimal("0"),
        )
    reported = _required_value(evidence[definition.reported_operand_id])
    variance = calculated - reported
    return OperatingIncomeValidationEvidence(
        definition.validation_id,
        definition.reported_operand_id,
        calculated,
        reported,
        variance,
        definition.expected_variance,
        definition.display_scale,
        variance == definition.expected_variance,
    )


def _required_value(evidence: OperatingIncomeOperandEvidence) -> Decimal:
    if evidence.expected_value is None:
        raise OperatingIncomeDerivationPolicyError(
            "Arithmetic referenced an explicitly absent operand"
        )
    return evidence.expected_value


def _context_cik(context: FilingXBRLContext) -> int | None:
    if (
        context.entity_identifier_scheme != "http://www.sec.gov/CIK"
        or not context.entity_identifier
        or not context.entity_identifier.isdigit()
    ):
        return None
    return int(context.entity_identifier)


def _normalized_unit(fact: FilingXBRLFact) -> str | None:
    unit = fact.unit
    if (
        fact.unit_ref is None
        or unit is None
        or unit.denominator_measures
        or len(unit.numerator_measures) != 1
    ):
        return None
    measure = unit.numerator_measures[0]
    return (
        "USD"
        if measure.namespace == _USD_NAMESPACE and measure.local_name == "USD"
        else None
    )


def _filing_evidence(
    occurrence: _Occurrence,
    filing_xbrl: SECFilingXBRL,
    ordinal: int,
) -> FilingXBRLEvidence:
    fact = occurrence.fact
    if not isinstance(fact.numeric_value, Decimal):
        raise OperatingIncomeDerivationPolicyError(
            "Operating Income evidence is not numeric"
        )
    return FilingXBRLEvidence(
        source_kind=EvidenceSourceKind.FILING_XBRL,
        source_url=fact.source_url,
        namespace=fact.namespace,
        concept=fact.concept,
        raw_value=fact.raw_value,
        value=fact.numeric_value,
        unit="USD",
        start=fact.start,
        end=fact.end,
        accession_number=fact.accession_number,
        observation_form=filing_xbrl.filing.form,
        observation_filed=filing_xbrl.filing.filing_date,
        filing_report_date=filing_xbrl.filing.report_date,
        primary_document=filing_xbrl.filing.primary_document,
        retrieved_at=filing_xbrl.retrieved_at,
        context_id=fact.context_id,
        dimensions=fact.dimensions,
        decimals=fact.decimals,
        is_nil=fact.is_nil,
        unit_ref=fact.unit_ref,
        occurrence_ordinal=ordinal,
        entity_identifier_scheme=occurrence.context.entity_identifier_scheme,
        entity_identifier=occurrence.context.entity_identifier,
    )
