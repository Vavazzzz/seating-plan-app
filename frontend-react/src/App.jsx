import React, { useEffect } from 'react'
import SectionList from './components/SectionList'
import CanvasStage from './components/CanvasStage'
import RowRangeDialog from './components/RowRangeDialog'
import { useStore } from './store/store'

export default function App() {
  const loadSections = useStore(state => state.loadSections)
  const selectedSection = useStore(state => state.selectedSection)

  useEffect(() => {
    loadSections()
  }, [])

  return (
    <div className="app">
      <aside className="sidebar">
        <SectionList />
      </aside>
      <main className="main">
        <div className="topbar">
          <h2>Seating Plan — React + Konva</h2>
        </div>
        <div className="canvas-area">
          <CanvasStage sectionName={selectedSection} />
        </div>
      </main>
      <RowRangeDialog />
    </div>
  )
}
