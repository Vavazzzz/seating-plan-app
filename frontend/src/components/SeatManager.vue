<template>
  <div class="panel">
    <h2>Seat Manager</h2>

    <div class="section">
      <h3>Add Seats to Section</h3>
      <div class="form-group">
        <select v-model="selectedSection" class="input">
          <option value="">-- Select Section --</option>
          <option v-for="section in sections" :key="section.name" :value="section.name">
            {{ section.name }}
          </option>
        </select>

        <input
          v-model="rowName"
          type="text"
          placeholder="Row name (e.g., A, 1, Row-1)"
          class="input"
        />

        <select v-model="seatMethod" class="input">
          <option value="single">Single Seat</option>
          <option value="bulk">Bulk Seats (comma-separated)</option>
          <option value="range">Range (A-Z or 1-100)</option>
        </select>
      </div>

      <div v-if="seatMethod === 'single'" class="form-group">
        <input v-model="singleSeat" type="text" placeholder="Seat number" class="input" />
        <button @click="addSingleSeat" class="btn btn-primary">Add</button>
      </div>

      <div v-if="seatMethod === 'bulk'" class="form-group">
        <input
          v-model="bulkSeats"
          type="text"
          placeholder="Seats (e.g., 1,2,3,4,5)"
          class="input"
        />
        <button @click="addBulkSeats" class="btn btn-primary">Add</button>
      </div>

      <div v-if="seatMethod === 'range'" class="form-group">
        <input v-model="rangeStart" type="text" placeholder="Start (e.g., A or 1)" class="input" />
        <input v-model="rangeEnd" type="text" placeholder="End (e.g., Z or 100)" class="input" />
        <button @click="addSeatRange" class="btn btn-primary">Add Range</button>
      </div>
    </div>

    <div class="section">
      <h3>Current Sections</h3>
      <div v-if="sections.length" class="sections-list">
        <div v-for="section in sections" :key="section.name" class="section-detail">
          <h4>{{ section.name }}</h4>

          <div v-if="section.rows.length" class="rows-container">
            <div v-for="row in section.rows" :key="row.row_number" class="row-section">
              <div class="row-header">
                <strong>{{ row.row_number }}</strong>
                <button @click="deleteRowWithConfirm(section.name, row.row_number)" class="btn btn-xs btn-danger">
                  Delete Row
                </button>
              </div>

              <div class="seats-grid">
                <div v-for="seat in row.seats" :key="seat.seat_number" class="seat-badge">
                  {{ seat.seat_number }}
                  <button
                    @click="deleteSeat(section.name, row.row_number, seat.seat_number)"
                    class="seat-delete"
                  >
                    ×
                  </button>
                </div>
              </div>
            </div>
          </div>
          <p v-else class="empty-state">No seats in this section</p>
        </div>
      </div>
      <p v-else class="empty-state">No sections. Create one first!</p>
    </div>

    <div v-if="message" :class="['message', message.type]">
      {{ message.text }}
    </div>
  </div>
</template>

<script>
import { ref, computed, onMounted } from 'vue'
import { sectionsAPI, seatsAPI } from '../api'

export default {
  name: 'SeatManager',
  setup() {
    const sections = ref([])
    const selectedSection = ref('')
    const rowName = ref('')
    const seatMethod = ref('single')
    const singleSeat = ref('')
    const bulkSeats = ref('')
    const rangeStart = ref('')
    const rangeEnd = ref('')
    const message = ref(null)

    const loadSections = async () => {
      try {
        const res = await sectionsAPI.list()
        sections.value = res.data || []
      } catch (err) {
        showMessage('Failed to load sections', 'error')
      }
    }

    const addSingleSeat = async () => {
      if (!selectedSection.value || !rowName.value || !singleSeat.value) {
        showMessage('All fields required', 'error')
        return
      }

      try {
        await seatsAPI.add(selectedSection.value, rowName.value, singleSeat.value)
        showMessage('Seat added', 'success')
        singleSeat.value = ''
        await loadSections()
      } catch (err) {
        showMessage('Failed to add seat', 'error')
      }
    }

    const addBulkSeats = async () => {
      if (!selectedSection.value || !rowName.value || !bulkSeats.value) {
        showMessage('All fields required', 'error')
        return
      }

      const seats = bulkSeats.value
        .split(',')
        .map((s) => s.trim())
        .filter((s) => s)
      if (!seats.length) return

      try {
        await sectionsAPI.bulkSeats(selectedSection.value, rowName.value, seats)
        showMessage(`${seats.length} seats added`, 'success')
        bulkSeats.value = ''
        await loadSections()
      } catch (err) {
        showMessage('Failed to add seats', 'error')
      }
    }

    const addSeatRange = async () => {
      if (!selectedSection.value || !rowName.value || !rangeStart.value || !rangeEnd.value) {
        showMessage('All fields required', 'error')
        return
      }

      try {
        await sectionsAPI.seatRange(selectedSection.value, rowName.value, rangeStart.value, rangeEnd.value)
        showMessage('Seat range added', 'success')
        rangeStart.value = ''
        rangeEnd.value = ''
        await loadSections()
      } catch (err) {
        showMessage('Failed to add seat range', 'error')
      }
    }

    const deleteSeat = async (section, row, seat) => {
      if (!confirm(`Delete seat ${seat}?`)) return

      try {
        await seatsAPI.delete(section, row, seat)
        showMessage('Seat deleted', 'success')
        await loadSections()
      } catch (err) {
        showMessage('Failed to delete seat', 'error')
      }
    }

    const deleteRowWithConfirm = async (section, row) => {
      if (!confirm(`Delete entire row "${row}"?`)) return

      try {
        await sectionsAPI.deleteRow(section, row)
        showMessage('Row deleted', 'success')
        await loadSections()
      } catch (err) {
        showMessage('Failed to delete row', 'error')
      }
    }

    const showMessage = (text, type = 'success') => {
      message.value = { text, type }
      setTimeout(() => (message.value = null), 3000)
    }

    onMounted(loadSections)

    return {
      sections,
      selectedSection,
      rowName,
      seatMethod,
      singleSeat,
      bulkSeats,
      rangeStart,
      rangeEnd,
      message,
      addSingleSeat,
      addBulkSeats,
      addSeatRange,
      deleteSeat,
      deleteRowWithConfirm,
    }
  },
}
</script>

<style scoped>
.panel {
  background: white;
  border-radius: 8px;
  padding: 2rem;
  box-shadow: 0 2px 4px rgba(0, 0, 0, 0.1);
}

.panel h2 {
  margin-top: 0;
  color: #333;
  border-bottom: 2px solid #667eea;
  padding-bottom: 1rem;
}

.section {
  margin-bottom: 2rem;
}

.section h3 {
  color: #555;
  margin-bottom: 1rem;
}

.section h4 {
  color: #667eea;
  margin-bottom: 0.75rem;
}

.form-group {
  display: flex;
  gap: 1rem;
  flex-wrap: wrap;
  margin-bottom: 1rem;
}

.input {
  flex: 1;
  min-width: 150px;
  padding: 0.75rem;
  border: 1px solid #ddd;
  border-radius: 4px;
  font-size: 1rem;
}

.input:focus {
  outline: none;
  border-color: #667eea;
  box-shadow: 0 0 0 3px rgba(102, 126, 234, 0.1);
}

.btn {
  padding: 0.75rem 1.5rem;
  border: none;
  border-radius: 4px;
  cursor: pointer;
  font-weight: 500;
  transition: all 0.3s ease;
}

.btn-primary {
  background: #667eea;
  color: white;
}

.btn-primary:hover {
  background: #5568d3;
}

.btn-danger {
  background: #f56565;
  color: white;
}

.btn-danger:hover {
  background: #e53e3e;
}

.btn-xs {
  padding: 0.3rem 0.6rem;
  font-size: 0.8rem;
}

.sections-list {
  display: flex;
  flex-direction: column;
  gap: 2rem;
}

.section-detail {
  border: 1px solid #e0e0e0;
  border-radius: 8px;
  padding: 1.5rem;
  background: #fafafa;
}

.rows-container {
  display: flex;
  flex-direction: column;
  gap: 1.5rem;
}

.row-section {
  background: white;
  border: 1px solid #e0e0e0;
  border-radius: 6px;
  padding: 1rem;
}

.row-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 1rem;
  padding-bottom: 0.5rem;
  border-bottom: 1px solid #e0e0e0;
}

.seats-grid {
  display: flex;
  flex-wrap: wrap;
  gap: 0.75rem;
}

.seat-badge {
  position: relative;
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  color: white;
  padding: 0.5rem 1rem;
  border-radius: 20px;
  font-weight: 500;
  font-size: 0.9rem;
  display: flex;
  align-items: center;
  gap: 0.5rem;
}

.seat-delete {
  background: rgba(255, 255, 255, 0.3);
  border: none;
  color: white;
  width: 20px;
  height: 20px;
  border-radius: 50%;
  cursor: pointer;
  display: flex;
  align-items: center;
  justify-content: center;
  font-weight: bold;
  transition: background 0.3s;
}

.seat-delete:hover {
  background: rgba(255, 255, 255, 0.5);
}

.empty-state {
  color: #999;
  text-align: center;
  padding: 1rem;
}

.message {
  padding: 1rem;
  border-radius: 4px;
  margin-top: 1rem;
}

.message.success {
  background: #c6f6d5;
  color: #22543d;
}

.message.error {
  background: #fed7d7;
  color: #742a2a;
}
</style>
