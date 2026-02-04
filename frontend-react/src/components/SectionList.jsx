import React, { useState } from 'react'
import { useStore } from '../store/store'

export default function SectionList(){
  const sections = useStore(state=>state.sections)
  const selectSection = useStore(state=>state.selectSection)
  const createSection = useStore(state=>state.createSection)
  const [newName, setNewName] = useState('')

  const onCreate = async () => {
    if(!newName.trim()) return
    try {
      // use API via store or direct call
      await fetch('/api/sections', { method:'POST', headers:{'Content-Type':'application/json'}, body:JSON.stringify({name:newName}) })
      await useStore.getState().loadSections()
      setNewName('')
    } catch(e){ console.error(e) }
  }

  return (
    <div className="section-list">
      <h3>Sections</h3>
      <div className="create-row">
        <input placeholder="New section" value={newName} onChange={e=>setNewName(e.target.value)} />
        <button onClick={onCreate}>Create</button>
      </div>
      <ul>
        {sections.map(s=> (
          <li key={s.name}>
            <button onClick={()=>selectSection(s.name)}>{s.name}</button>
          </li>
        ))}
      </ul>
    </div>
  )
}
