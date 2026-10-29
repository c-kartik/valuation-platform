import {it,expect,vi} from 'vitest';
import {render,screen} from '@testing-library/react';
import {ExportData} from './ExportData';
import {StrictMode} from 'react';
it('exports exact strings/provenance and keeps the Strict Mode URL live until replacement/unmount',async()=>{
 let sequence=0;
 const create=vi.spyOn(URL,'createObjectURL').mockImplementation(()=>`blob:fixture-${++sequence}`),revoke=vi.spyOn(URL,'revokeObjectURL');
 const value={amount:'1.23456789123456789123456789',source:{url:'https://www.sec.gov/example',unknown:null}};
 const view=render(<StrictMode><ExportData value={value} name="Software / test"/></StrictMode>);expect(screen.getByRole('link',{name:'Download calculation data'}).getAttribute('download')).toBe('Software---test.json');
 const active=screen.getByRole('link').getAttribute('href');expect(create).toHaveBeenCalledTimes(2);expect(active).toBe('blob:fixture-2');expect(revoke).toHaveBeenCalledWith('blob:fixture-1');expect(revoke).not.toHaveBeenCalledWith(active);
 const blob=create.mock.calls[0][0] as Blob;
 const text=await new Promise<string>(resolve=>{const reader=new FileReader();reader.onload=()=>resolve(String(reader.result));reader.readAsText(blob);});expect(JSON.parse(text)).toEqual(value);expect(text).toContain(value.amount);
 const changed={...value,amount:'2.000000000000000000001'};view.rerender(<StrictMode><ExportData value={changed} name="Software / test"/></StrictMode>);expect(revoke).toHaveBeenCalledWith(active);const latest=screen.getByRole('link').getAttribute('href');expect(latest).toBe('blob:fixture-3');expect(revoke).not.toHaveBeenCalledWith(latest);view.unmount();expect(revoke).toHaveBeenCalledWith(latest);create.mockRestore();revoke.mockRestore();
});
