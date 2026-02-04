import React, { useState } from 'react'
import { useStore } from '../store/store'

export default function RowRangeDialog(){
  const [open, setOpen] = useState(false)
  const selectedSection = useStore(s=>s.selectedSection)
  const addRowRange = useStore(s=>s.addRowRange)

  // Expose a global toggle via window for simplicity in this draft
  window.openRowRange = () => setOpen(true)

  const [form, setForm] = useState({
    startRow:'', endRow:'', startSeat:'1', endSeat:'10', parity:'all', rowPrefix:'', rowSuffix:'', unnumberedRows:false, continuous:false
  })

  const submit = async () => {
    await addRowRange({
      start_row: form.startRow,
      end_row: form.endRow,
      start_seat: form.startSeat,
      end_seat: form.endSeat,
      parity: form.parity,
      row_prefix: form.rowPrefix,
      row_suffix: form.rowSuffix,
      unnumbered_rows: form.unnumberedRows,
      continuous: form.continuous
    })
    setOpen(false)
  }

  if(!open) return null
  return (
    <div className="dialog-overlay">
      <div className="dialog">
        <h4>Add Row Range</h4>
        <label>Start Row<input value={form.startRow} onChange={e=>setForm({...form, startRow:e.target.value})} /></label>
        <label>End Row<input value={form.endRow} onChange={e=>setForm({...form, endRow:e.target.value})} /></label>
        <label>Start Seat<input value={form.startSeat} onChange={e=>setForm({...form, startSeat:e.target.value})} /></label>
        <label>End Seat<input value={form.endSeat} onChange={e=>setForm({...form, endSeat:e.target.value})} /></label>
        <label>Parity<select value={form.parity} onChange={e=>setForm({...form, parity:e.target.value})}><option value="all">All</option><option value="even">Even</option><option value="odd">Odd</option></select></label>
        <label>Prefix<input value={form.rowPrefix} onChange={e=>setForm({...form, rowPrefix:e.target.value})} /></label>
        <label>Suffix<input value={form.rowSuffix} onChange={e=>setForm({...form, rowSuffix:e.target.value})} /></label>
        <label><input type="checkbox" checked={form.unnumberedRows} onChange={e=>setForm({...form, unnumberedRows:e.target.checked})} /> Unnumbered Rows</label>
        <label><input type="checkbox" checked={form.continuous} onChange={e=>setForm({...form, continuous:e.target.checked})} /> Continuous</label>
        <div className="actions"><button onClick={submit}>Add</button><button onClick={()=>setOpen(false)}>Cancel</button></div>
      </div>
    </div>
  )
}
