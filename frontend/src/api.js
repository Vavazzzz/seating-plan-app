import axios from 'axios'

const API_BASE = 'http://localhost:8000/api'

const api = axios.create({
  baseURL: API_BASE,
  headers: {
    'Content-Type': 'application/json',
  },
})

export const projectsAPI = {
  new: (name) => api.post(`/projects/new/${name}`),
  save: (name) => api.post('/projects/save', { name }),
  load: (name) => api.post('/projects/load', { name }),
  list: () => api.get('/projects/list'),
  delete: (name) => api.delete(`/projects/${name}`),
}

export const sectionsAPI = {
  list: () => api.get('/sections'),
  get: (name) => api.get(`/sections/${name}`),
  create: (name, isGa = false) => api.post('/sections', { name, is_ga: isGa }),
  delete: (name) => api.delete(`/sections/${name}`),
  rename: (name, newName) => api.patch(`/sections/${name}`, { new_name: newName }),
  clone: (name, count = 1) => api.post(`/sections/${name}/clone?count=${count}`),
  bulkSeats: (name, row, seatNumbers) =>
    api.post(`/sections/${name}/rows/${row}/bulk`, { seat_numbers: seatNumbers }),
  seatRange: (name, row, startSeat, endSeat) =>
    api.post(`/sections/${name}/rows/${row}/range`, { start_seat: startSeat, end_seat: endSeat }),
  deleteRow: (name, row) => api.delete(`/sections/${name}/rows/${row}`),
}

export const seatsAPI = {
  list: (section) => api.get(`/seats/${section}`),
  add: (section, row, seatNumber) => api.post(`/seats/${section}/${row}`, { seat_number: seatNumber }),
  delete: (section, row, seat) => api.delete(`/seats/${section}/${row}/${seat}`),
}

export default api
