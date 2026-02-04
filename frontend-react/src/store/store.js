import create from 'zustand'
import produce from 'immer'
import { sectionsAPI, seatsAPI } from '../api'

// Simple undo/redo store using history stacks
export const useStore = create((set, get) => ({
  // app state
  sections: [],
  selectedSection: '',
  sectionData: null, // current section details { name, rows: [{ row_number, seats: [{seat_number}]}] }

  // history
  past: [],
  future: [],

  // load list of sections
  loadSections: async () => {
    const res = await sectionsAPI.list()
    set({ sections: res.data || [] })
  },

  // select section and fetch data
  selectSection: async (name) => {
    const res = await sectionsAPI.get(name)
    set({ selectedSection: name, sectionData: res.data || null, past: [], future: [] })
  },

  // local helper to snapshot state for undo
  snapshot: () => {
    const s = get().sectionData
    get().past.push(JSON.parse(JSON.stringify(s)))
    // clear future when new action
    set({ future: [] })
  },

  // undo
  undo: () => {
    const { past, future, sectionData } = get()
    if (!past || past.length === 0) return
    const previous = past.pop()
    future.push(JSON.parse(JSON.stringify(sectionData)))
    set({ sectionData: previous, past, future })
  },

  // redo
  redo: () => {
    const { past, future, sectionData } = get()
    if (!future || future.length === 0) return
    const next = future.pop()
    past.push(JSON.parse(JSON.stringify(sectionData)))
    set({ sectionData: next, past, future })
  },

  // add seat (local + API)
  addSeat: async (row, seat) => {
    const sectionName = get().selectedSection
    if (!sectionName) return
    get().snapshot()
    try {
      await seatsAPI.add(sectionName, row, seat)
      // update local state
      set(produce(state => {
        if (!state.sectionData) return
        let rowObj = state.sectionData.rows.find(r => r.row_number === row)
        if (!rowObj) {
          rowObj = { row_number: row, seats: [] }
          state.sectionData.rows.push(rowObj)
        }
        if (!rowObj.seats.find(s => s.seat_number === seat)) {
          rowObj.seats.push({ seat_number: seat })
        }
      }))
    } catch (err) {
      console.error(err)
    }
  },

  // delete seat
  deleteSeat: async (row, seat) => {
    const sectionName = get().selectedSection
    if (!sectionName) return
    get().snapshot()
    try {
      await seatsAPI.delete(sectionName, row, seat)
      set(produce(state => {
        if (!state.sectionData) return
        const rowObj = state.sectionData.rows.find(r => r.row_number === row)
        if (!rowObj) return
        rowObj.seats = rowObj.seats.filter(s => s.seat_number !== seat)
      }))
    } catch (err) {
      console.error(err)
    }
  },

  // add row range via sections API
  addRowRange: async (payload) => {
    const sectionName = get().selectedSection
    if (!sectionName) return
    get().snapshot()
    try {
      await sectionsAPI.seatRange(sectionName, payload)
      // refresh section
      const res = await sectionsAPI.get(sectionName)
      set({ sectionData: res.data || null })
    } catch (err) {
      console.error(err)
    }
  }
}))
