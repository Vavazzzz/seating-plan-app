import axios from 'axios'

const API_BASE = '/api'
const api = axios.create({ baseURL: API_BASE, headers: { 'Content-Type': 'application/json' } })

export const sectionsAPI = {
  list: () => api.get('/sections'),
  get: (name) => api.get(`/sections/${encodeURIComponent(name)}`),
  create: (name, isGa = false) => api.post('/sections', { name, is_ga: isGa }),
  delete: (name) => api.delete(`/sections/${encodeURIComponent(name)}`),
  rename: (name, newName) => api.patch(`/sections/${encodeURIComponent(name)}`, { new_name: newName }),
  clone: (name, count = 1) => api.post(`/sections/${encodeURIComponent(name)}/clone?count=${count}`),
  bulkSeats: (name, row, seatNumbers) => api.post(`/sections/${encodeURIComponent(name)}/rows/${encodeURIComponent(row)}/bulk`, { seat_numbers: seatNumbers }),
  seatRange: (name, payload) => api.post(`/sections/${encodeURIComponent(name)}/rows/range`, payload),
  deleteRow: (name, row) => api.delete(`/sections/${encodeURIComponent(name)}/rows/${encodeURIComponent(row)}`),
}

export const seatsAPI = {
  list: (section) => api.get(`/seats/${encodeURIComponent(section)}`),
  add: (section, row, seatNumber) => api.post(`/seats/${encodeURIComponent(section)}/${encodeURIComponent(row)}`, { seat_number: seatNumber }),
  delete: (section, row, seat) => api.delete(`/seats/${encodeURIComponent(section)}/${encodeURIComponent(row)}/${encodeURIComponent(seat)}`),
}

export default api
