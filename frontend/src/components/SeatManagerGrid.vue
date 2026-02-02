<template>
  <div class="seat-manager">
    <!-- Section selector -->
    <div class="section-selector">
      <label>Section:</label>
      <select v-model="selectedSection" class="input" @change="loadSection">
        <option value="">-- Select Section --</option>
        <option v-for="section in sections" :key="section.name" :value="section.name">
          {{ section.name }}
        </option>
      </select>
    </div>

    <!-- Controls -->
    <div class="controls" v-if="selectedSection">
      <button @click="showRowRangeDialog" class="btn btn-primary">➕ Add Row Range</button>
      <button @click="showSingleSeatDialog" class="btn btn-primary">➕ Add Seat</button>
      <button @click="deleteSelectedSeats" class="btn btn-danger" :disabled="selectedSeats.length === 0">🗑️ Delete Selected (Del)</button>
      <button @click="selectAllSeats" class="btn btn-secondary" title="Ctrl+A">Select All</button>
      <button @click="clearSelection" class="btn btn-secondary" title="Escape">Clear Selection</button>
      <button @click="saveChanges" class="btn btn-success">💾 Save</button>
    </div>

    <!-- Grid visualization -->
    <div class="grid-container" v-if="selectedSection && currentSection" @keydown="handleKeydown">
      <div class="grid-wrapper">
        <div class="row-labels">
          <div class="row-label-spacer"></div>
          <div v-for="row in sortedRows" :key="row" class="row-label">
            {{ row }}
          </div>
        </div>
        
        <div class="grid">
          <div v-for="seatNum in allSeatNumbers" :key="seatNum" class="seat-column">
            <div class="column-header">{{ seatNum }}</div>
            <div
              v-for="row in sortedRows"
              :key="`${row}-${seatNum}`"
              :class="[
                'seat',
                { 
                  'seat-exists': hasSeat(row, seatNum),
                  'seat-selected': isSeatSelected(row, seatNum),
                  'seat-hover': hoverSeat === `${row}-${seatNum}`
                }
              ]"
              @click="toggleSeatSelection(row, seatNum, $event)"
              @mouseenter="hoverSeat = `${row}-${seatNum}`"
              @mouseleave="hoverSeat = null"
              @mousedown="startDragSelection(row, seatNum, $event)"
            >
              <span v-if="hasSeat(row, seatNum)" class="seat-number">{{ seatNum }}</span>
            </div>
          </div>
        </div>
      </div>
    </div>

    <!-- Row Range Dialog -->
    <div v-if="showRowRangeModal" class="modal-overlay" @click.self="closeRowRangeDialog">
      <div class="modal">
        <h3>Add Row Range</h3>
        <form @submit.prevent="submitRowRange">
          <div class="form-group">
            <label>Start Row:</label>
            <input v-model="rowRangeForm.startRow" type="text" placeholder="e.g., 1 or A" class="input" required />
          </div>
          <div class="form-group">
            <label>End Row:</label>
            <input v-model="rowRangeForm.endRow" type="text" placeholder="e.g., 10 or F" class="input" required />
          </div>
          <div class="form-group">
            <label>Start Seat:</label>
            <input v-model="rowRangeForm.startSeat" type="text" placeholder="e.g., 1 or A" class="input" required />
          </div>
          <div class="form-group">
            <label>End Seat:</label>
            <input v-model="rowRangeForm.endSeat" type="text" placeholder="e.g., 10 or Z" class="input" required />
          </div>
          <div class="form-group">
            <label>Seat Filter:</label>
            <select v-model="rowRangeForm.parity" class="input">
              <option value="all">All</option>
              <option value="even">Even</option>
              <option value="odd">Odd</option>
            </select>
          </div>
          <div class="form-group">
            <label>Row Prefix:</label>
            <input v-model="rowRangeForm.rowPrefix" type="text" placeholder="Optional" class="input" />
          </div>
          <div class="form-group">
            <label>Row Suffix:</label>
            <input v-model="rowRangeForm.rowSuffix" type="text" placeholder="Optional" class="input" />
          </div>
          <div class="checkbox-group">
            <label>
              <input v-model="rowRangeForm.unnumberedRows" type="checkbox" />
              Unnumbered Rows (# prefix)
            </label>
          </div>
          <div class="checkbox-group">
            <label>
              <input v-model="rowRangeForm.continuous" type="checkbox" />
              Continuous Numbering (numeric seats only)
            </label>
          </div>
          <div class="form-actions">
            <button type="submit" class="btn btn-primary">Add Rows</button>
            <button type="button" @click="closeRowRangeDialog" class="btn btn-secondary">Cancel</button>
          </div>
        </form>
      </div>
    </div>

    <!-- Single Seat Dialog -->
    <div v-if="showSingleSeatModal" class="modal-overlay" @click.self="closeSingleSeatDialog">
      <div class="modal">
        <h3>Add Single Seat</h3>
        <form @submit.prevent="submitSingleSeat">
          <div class="form-group">
            <label>Row:</label>
            <input v-model="singleSeatForm.row" type="text" placeholder="Row name" class="input" required />
          </div>
          <div class="form-group">
            <label>Seat Number:</label>
            <input v-model="singleSeatForm.seatNumber" type="text" placeholder="Seat number" class="input" required />
          </div>
          <div class="form-actions">
            <button type="submit" class="btn btn-primary">Add Seat</button>
            <button type="button" @click="closeSingleSeatDialog" class="btn btn-secondary">Cancel</button>
          </div>
        </form>
      </div>
    </div>

    <!-- Message -->
    <div v-if="message" :class="['message', message.type]">
      {{ message.text }}
    </div>
  </div>
</template>

<script>
import { ref, computed, onMounted, onUnmounted } from 'vue'
import { sectionsAPI, seatsAPI } from '../api'

export default {
  name: 'SeatManagerGrid',
  setup() {
    const sections = ref([])
    const selectedSection = ref('')
    const currentSection = ref(null)
    const selectedSeats = ref(new Set())
    const hoverSeat = ref(null)
    const message = ref(null)
    
    // Row range dialog
    const showRowRangeModal = ref(false)
    const rowRangeForm = ref({
      startRow: '',
      endRow: '',
      startSeat: '1',
      endSeat: '10',
      parity: 'all',
      rowPrefix: '',
      rowSuffix: '',
      unnumberedRows: false,
      continuous: false
    })
    
    // Single seat dialog
    const showSingleSeatModal = ref(false)
    const singleSeatForm = ref({
      row: '',
      seatNumber: ''
    })
    
    // Drag selection
    let dragStart = null
    let isDragging = false

    const sortedRows = computed(() => {
      if (!currentSection.value) return []
      const rowSet = new Set()
      currentSection.value.rows.forEach(row => rowSet.add(row.row_number))
      return Array.from(rowSet).sort((a, b) => {
        // Try numeric sort, fallback to alpha
        const numA = parseInt(a)
        const numB = parseInt(b)
        if (!isNaN(numA) && !isNaN(numB)) return numA - numB
        return a.localeCompare(b)
      })
    })

    const allSeatNumbers = computed(() => {
      if (!currentSection.value) return []
      const seatSet = new Set()
      currentSection.value.rows.forEach(row => {
        row.seats.forEach(seat => seatSet.add(seat.seat_number))
      })
      const arr = Array.from(seatSet)
      // Try numeric sort
      try {
        return arr.sort((a, b) => {
          const numA = parseInt(a)
          const numB = parseInt(b)
          if (!isNaN(numA) && !isNaN(numB)) return numA - numB
          return a.localeCompare(b)
        })
      } catch {
        return arr.sort()
      }
    })

    const loadSections = async () => {
      try {
        const res = await sectionsAPI.list()
        sections.value = res.data || []
      } catch (err) {
        showMessage('Failed to load sections', 'error')
      }
    }

    const loadSection = async () => {
      if (!selectedSection.value) {
        currentSection.value = null
        return
      }
      try {
        const res = await sectionsAPI.get(selectedSection.value)
        currentSection.value = res.data
        selectedSeats.value.clear()
      } catch (err) {
        showMessage('Failed to load section', 'error')
      }
    }

    const hasSeat = (row, seatNum) => {
      if (!currentSection.value) return false
      return currentSection.value.rows.some(r => 
        r.row_number === row && r.seats.some(s => s.seat_number === seatNum)
      )
    }

    const isSeatSelected = (row, seatNum) => {
      return selectedSeats.value.has(`${row}-${seatNum}`)
    }

    const toggleSeatSelection = (row, seatNum, event) => {
      if (!hasSeat(row, seatNum)) return
      const key = `${row}-${seatNum}`
      if (event.ctrlKey || event.metaKey) {
        if (selectedSeats.value.has(key)) {
          selectedSeats.value.delete(key)
        } else {
          selectedSeats.value.add(key)
        }
      } else if (event.shiftKey) {
        // Shift-click: select range (simple impl)
        if (selectedSeats.value.size === 0) {
          selectedSeats.value.add(key)
        } else {
          selectedSeats.value.add(key)
        }
      } else {
        selectedSeats.value.clear()
        selectedSeats.value.add(key)
      }
    }

    const startDragSelection = (row, seatNum, event) => {
      if (event.button !== 0) return // left click only
      if (!hasSeat(row, seatNum)) return
      isDragging = true
      dragStart = { row, seatNum }
      selectedSeats.value.clear()
      selectedSeats.value.add(`${row}-${seatNum}`)
    }

    const handleMouseMove = (event) => {
      if (!isDragging || !dragStart) return
      // Drag selection is handled by hover + click logic
      // For now, we'll use a simpler approach via shift-click
    }

    const handleMouseUp = () => {
      isDragging = false
      dragStart = null
    }

    const selectAllSeats = () => {
      selectedSeats.value.clear()
      if (currentSection.value) {
        currentSection.value.rows.forEach(row => {
          row.seats.forEach(seat => {
            selectedSeats.value.add(`${row.row_number}-${seat.seat_number}`)
          })
        })
      }
    }

    const clearSelection = () => {
      selectedSeats.value.clear()
    }

    const deleteSelectedSeats = async () => {
      if (selectedSeats.value.size === 0) return
      if (!confirm(`Delete ${selectedSeats.value.size} seat(s)?`)) return

      try {
        for (const key of selectedSeats.value) {
          const [row, seat] = key.split('-')
          await seatsAPI.delete(selectedSection.value, row, seat)
        }
        showMessage(`${selectedSeats.value.size} seat(s) deleted`, 'success')
        selectedSeats.value.clear()
        await loadSection()
      } catch (err) {
        showMessage('Failed to delete seats', 'error')
      }
    }

    const showRowRangeDialog = () => {
      rowRangeForm.value = {
        startRow: '',
        endRow: '',
        startSeat: '1',
        endSeat: '10',
        parity: 'all',
        rowPrefix: '',
        rowSuffix: '',
        unnumberedRows: false,
        continuous: false
      }
      showRowRangeModal.value = true
    }

    const closeRowRangeDialog = () => {
      showRowRangeModal.value = false
    }

    const submitRowRange = async () => {
      if (!selectedSection.value) return
      const { startRow, endRow, startSeat, endSeat, parity, rowPrefix, rowSuffix, unnumberedRows, continuous } = rowRangeForm.value
      if (!startRow || !endRow || !startSeat || !endSeat) {
        showMessage('All fields required', 'error')
        return
      }

      try {
        const payload = {
          start_row: startRow,
          end_row: endRow,
          start_seat: startSeat,
          end_seat: endSeat,
          parity: parity,
          row_prefix: rowPrefix,
          row_suffix: rowSuffix,
          unnumbered_rows: unnumberedRows,
          continuous: continuous
        }
        const res = await fetch(`/api/sections/${selectedSection.value}/rows/range`, {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify(payload)
        })
        if (!res.ok) throw new Error(await res.text())
        showMessage('Row range added', 'success')
        closeRowRangeDialog()
        await loadSection()
      } catch (err) {
        showMessage('Failed to add row range', 'error')
      }
    }

    const showSingleSeatDialog = () => {
      singleSeatForm.value = { row: '', seatNumber: '' }
      showSingleSeatModal.value = true
    }

    const closeSingleSeatDialog = () => {
      showSingleSeatModal.value = false
    }

    const submitSingleSeat = async () => {
      if (!selectedSection.value) return
      const { row, seatNumber } = singleSeatForm.value
      if (!row || !seatNumber) {
        showMessage('All fields required', 'error')
        return
      }

      try {
        await seatsAPI.add(selectedSection.value, row, seatNumber)
        showMessage('Seat added', 'success')
        closeSingleSeatDialog()
        await loadSection()
      } catch (err) {
        showMessage('Failed to add seat', 'error')
      }
    }

    const saveChanges = async () => {
      // Changes are auto-saved when added/deleted
      showMessage('All changes saved', 'success')
    }

    const handleKeydown = (event) => {
      if (event.key === 'Delete') {
        deleteSelectedSeats()
      } else if (event.ctrlKey && event.key === 'a') {
        event.preventDefault()
        selectAllSeats()
      } else if (event.key === 'Escape') {
        clearSelection()
      }
    }

    const showMessage = (text, type = 'success') => {
      message.value = { text, type }
      setTimeout(() => (message.value = null), 3000)
    }

    onMounted(() => {
      loadSections()
      document.addEventListener('mousemove', handleMouseMove)
      document.addEventListener('mouseup', handleMouseUp)
    })

    onUnmounted(() => {
      document.removeEventListener('mousemove', handleMouseMove)
      document.removeEventListener('mouseup', handleMouseUp)
    })

    return {
      sections,
      selectedSection,
      currentSection,
      selectedSeats,
      hoverSeat,
      message,
      showRowRangeModal,
      rowRangeForm,
      showSingleSeatModal,
      singleSeatForm,
      sortedRows,
      allSeatNumbers,
      loadSection,
      hasSeat,
      isSeatSelected,
      toggleSeatSelection,
      startDragSelection,
      selectAllSeats,
      clearSelection,
      deleteSelectedSeats,
      showRowRangeDialog,
      closeRowRangeDialog,
      submitRowRange,
      showSingleSeatDialog,
      closeSingleSeatDialog,
      submitSingleSeat,
      saveChanges,
      handleKeydown
    }
  }
}
</script>

<style scoped>
.seat-manager {
  background: white;
  border-radius: 8px;
  padding: 2rem;
  box-shadow: 0 2px 4px rgba(0, 0, 0, 0.1);
}

.section-selector {
  display: flex;
  gap: 1rem;
  align-items: center;
  margin-bottom: 2rem;
}

.section-selector label {
  font-weight: 500;
}

.section-selector .input {
  flex: 1;
  max-width: 300px;
  padding: 0.75rem;
  border: 1px solid #ddd;
  border-radius: 4px;
  font-size: 1rem;
}

.controls {
  display: flex;
  gap: 1rem;
  margin-bottom: 2rem;
  flex-wrap: wrap;
}

.btn {
  padding: 0.75rem 1.5rem;
  border: none;
  border-radius: 4px;
  cursor: pointer;
  font-weight: 500;
  transition: all 0.3s ease;
  font-size: 0.9rem;
}

.btn-primary {
  background: #667eea;
  color: white;
}

.btn-primary:hover {
  background: #5568d3;
}

.btn-primary:disabled {
  background: #ccc;
  cursor: not-allowed;
}

.btn-danger {
  background: #f56565;
  color: white;
}

.btn-danger:hover {
  background: #e53e3e;
}

.btn-danger:disabled {
  background: #ccc;
  cursor: not-allowed;
}

.btn-secondary {
  background: #e0e0e0;
  color: #333;
}

.btn-secondary:hover {
  background: #d0d0d0;
}

.btn-success {
  background: #48bb78;
  color: white;
}

.btn-success:hover {
  background: #38a169;
}

.grid-container {
  border: 1px solid #e0e0e0;
  border-radius: 8px;
  padding: 1rem;
  background: #fafafa;
  overflow-x: auto;
  outline: none;
}

.grid-wrapper {
  display: flex;
  gap: 1rem;
}

.row-labels {
  display: flex;
  flex-direction: column;
  gap: 0;
}

.row-label-spacer {
  height: 30px;
  font-weight: 600;
  display: flex;
  align-items: center;
  justify-content: center;
}

.row-label {
  height: 30px;
  font-weight: 600;
  display: flex;
  align-items: center;
  justify-content: center;
  min-width: 40px;
  background: #f0f0f0;
  border-radius: 4px;
  border: 1px solid #ddd;
  font-size: 0.9rem;
}

.grid {
  display: flex;
  gap: 0.5rem;
}

.seat-column {
  display: flex;
  flex-direction: column;
  gap: 0;
}

.column-header {
  height: 30px;
  font-weight: 600;
  display: flex;
  align-items: center;
  justify-content: center;
  min-width: 30px;
  background: #f0f0f0;
  border-radius: 4px;
  border: 1px solid #ddd;
  font-size: 0.8rem;
}

.seat {
  width: 30px;
  height: 30px;
  border: 1px solid #ddd;
  border-radius: 4px;
  display: flex;
  align-items: center;
  justify-content: center;
  cursor: pointer;
  background: #fff;
  transition: all 0.2s ease;
  font-size: 0.7rem;
}

.seat:not(.seat-exists) {
  cursor: not-allowed;
  background: #fafafa;
  border-color: #f0f0f0;
}

.seat-exists {
  background: #e8f5e9;
  border-color: #4caf50;
  cursor: pointer;
}

.seat-exists:hover {
  background: #c8e6c9;
}

.seat-selected {
  background: #667eea;
  color: white;
  border-color: #5568d3;
  font-weight: bold;
}

.seat-selected .seat-number {
  color: white;
}

.seat-hover.seat-exists {
  box-shadow: 0 0 0 2px #667eea;
}

.seat-number {
  color: #333;
  font-weight: 600;
}

.modal-overlay {
  position: fixed;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background: rgba(0, 0, 0, 0.5);
  display: flex;
  align-items: center;
  justify-content: center;
  z-index: 1000;
}

.modal {
  background: white;
  border-radius: 8px;
  padding: 2rem;
  max-width: 500px;
  width: 90%;
  max-height: 80vh;
  overflow-y: auto;
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.15);
}

.modal h3 {
  margin-top: 0;
  color: #333;
  margin-bottom: 1.5rem;
}

.form-group {
  margin-bottom: 1.5rem;
}

.form-group label {
  display: block;
  font-weight: 500;
  margin-bottom: 0.5rem;
  color: #555;
}

.form-group .input {
  width: 100%;
  padding: 0.75rem;
  border: 1px solid #ddd;
  border-radius: 4px;
  font-size: 1rem;
}

.form-group .input:focus {
  outline: none;
  border-color: #667eea;
  box-shadow: 0 0 0 3px rgba(102, 126, 234, 0.1);
}

.checkbox-group {
  margin-bottom: 1rem;
}

.checkbox-group label {
  display: flex;
  align-items: center;
  gap: 0.5rem;
  cursor: pointer;
  color: #555;
  font-weight: 400;
}

.checkbox-group input {
  cursor: pointer;
}

.form-actions {
  display: flex;
  gap: 1rem;
  justify-content: flex-end;
}

.form-actions .btn {
  flex: 1;
}

.message {
  padding: 1rem;
  border-radius: 4px;
  margin-top: 1.5rem;
  font-weight: 500;
}

.message.success {
  background: #c6f6d5;
  color: #22543d;
  border: 1px solid #9ae6b4;
}

.message.error {
  background: #fed7d7;
  color: #742a2a;
  border: 1px solid #fc8181;
}
</style>
