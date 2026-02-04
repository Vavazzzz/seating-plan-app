import React, { useRef, useEffect, useState } from 'react'
import { Stage, Layer, Rect, Text, Group } from 'react-konva'
import { useStore } from '../store/store'

const CELL = 40
const PADDING = 20

export default function CanvasStage({ sectionName }) {
  const sectionData = useStore(state => state.sectionData)
  const addSeat = useStore(state => state.addSeat)
  const deleteSeat = useStore(state => state.deleteSeat)

  const [selected, setSelected] = useState(new Set())

  useEffect(() => {
    setSelected(new Set())
  }, [sectionName])

  if (!sectionName) return <div className="empty">Select a section</div>
  if (!sectionData) return <div className="empty">Loading...</div>

  const rows = sectionData.rows.map(r => r.row_number)
  const seatNumsSet = new Set()
  sectionData.rows.forEach(r => r.seats.forEach(s => seatNumsSet.add(s.seat_number)))
  const seatNums = Array.from(seatNumsSet).sort((a,b)=>{
    const na = parseInt(a); const nb = parseInt(b)
    if(!isNaN(na) && !isNaN(nb)) return na-nb
    return a.localeCompare(b)
  })

  const width = PADDING*2 + seatNums.length * CELL
  const height = PADDING*2 + rows.length * CELL

  const hasSeat = (row, seat) => {
    const r = sectionData.rows.find(rr => rr.row_number === row)
    if(!r) return false
    return r.seats.some(s => s.seat_number === seat)
  }

  const handleCellClick = (row, seat, e) => {
    const key = `${row}-${seat}`
    const set = new Set(selected)
    if (set.has(key)) set.delete(key)
    else set.add(key)
    setSelected(set)
  }

  const handleDoubleClick = (row, seat) => {
    if (!hasSeat(row, seat)) {
      addSeat(row, seat)
    }
  }

  const renderCell = (row, seat, i, j) => {
    const x = PADDING + j * CELL
    const y = PADDING + i * CELL
    const key = `${row}-${seat}`
    const exists = hasSeat(row, seat)
    const isSel = selected.has(key)
    return (
      <Group key={key} x={x} y={y}>
        <Rect
          width={CELL-4}
          height={CELL-4}
          cornerRadius={4}
          stroke={exists ? '#4caf50' : '#ddd'}
          fill={isSel ? '#667eea' : (exists ? '#e8f5e9' : '#fff')}
          onClick={(e) => handleCellClick(row, seat, e)}
          onDblClick={(e) => handleDoubleClick(row, seat)}
        />
        {exists && (
          <Text text={seat} x={6} y={6} fontSize={12} fill={isSel ? '#fff' : '#333'} />
        )}
      </Group>
    )
  }

  return (
    <div className="konva-wrap">
      <Stage width={Math.max(window.innerWidth - 320, width)} height={Math.min(800, height)}>
        <Layer>
          {/* column headers */}
          {seatNums.map((s, j) => (
            <Text key={`h-${s}`} text={s} x={PADDING + j * CELL + 6} y={4} fontSize={12} fontStyle={'bold'} />
          ))}

          {/* row labels */}
          {rows.map((r, i) => (
            <Text key={`r-${r}`} text={r} x={4} y={PADDING + i * CELL + 6} fontSize={12} fontStyle={'bold'} />
          ))}

          {/* seats grid */}
          {rows.map((r, i) => seatNums.map((s, j) => renderCell(r, s, i, j))) }
        </Layer>
      </Stage>
    </div>
  )
}
