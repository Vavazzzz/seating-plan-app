<template>
  <div class="panel">
    <h2>Section Manager</h2>

    <div class="section">
      <h3>Create Section</h3>
      <div class="form-group">
        <input
          v-model="newSectionName"
          type="text"
          placeholder="Section name"
          class="input"
        />
        <label class="checkbox">
          <input type="checkbox" v-model="newSectionIsGa" />
          General Admission
        </label>
        <button @click="createSection" class="btn btn-primary">Create</button>
      </div>
    </div>

    <div class="section">
      <h3>Sections</h3>
      <div v-if="sections.length" class="sections-grid">
        <div v-for="section in sections" :key="section.name" class="section-card">
          <div class="section-header">
            <h4>{{ section.name }}</h4>
            <span v-if="section.is_ga" class="badge-ga">GA</span>
          </div>

          <div class="section-stats">
            <span>Rows: {{ section.rows.length }}</span>
            <span>Seats: {{ totalSeats(section) }}</span>
          </div>

          <div class="section-actions">
            <button @click="showRenameForm(section.name)" class="btn btn-sm">Rename</button>
            <button @click="cloneSection(section.name)" class="btn btn-sm">Clone</button>
            <button @click="deleteSection(section.name)" class="btn btn-sm btn-danger">Delete</button>
          </div>

          <div v-if="renamingSection === section.name" class="rename-form">
            <input
              v-model="newName"
              type="text"
              placeholder="New name"
              class="input-sm"
              @keyup.enter="renameSection"
            />
            <button @click="renameSection" class="btn btn-sm btn-success">Save</button>
            <button @click="renamingSection = null" class="btn btn-sm">Cancel</button>
          </div>

          <details class="rows-detail">
            <summary>View Rows</summary>
            <div class="rows-list">
              <div v-for="row in section.rows" :key="row.row_number" class="row-item">
                <strong>{{ row.row_number }}:</strong>
                {{ row.seats.map((s) => s.seat_number).join(', ') }}
                <button @click="deleteRow(section.name, row.row_number)" class="btn btn-xs">Delete</button>
              </div>
            </div>
          </details>
        </div>
      </div>
      <p v-else class="empty-state">No sections. Create one above!</p>
    </div>

    <div v-if="message" :class="['message', message.type]">
      {{ message.text }}
    </div>
  </div>
</template>

<script>
import { ref, onMounted } from 'vue'
import { sectionsAPI } from '../api'

export default {
  name: 'SectionManager',
  setup() {
    const sections = ref([])
    const newSectionName = ref('')
    const newSectionIsGa = ref(false)
    const renamingSection = ref(null)
    const newName = ref('')
    const message = ref(null)

    const loadSections = async () => {
      try {
        const res = await sectionsAPI.list()
        sections.value = res.data || []
      } catch (err) {
        showMessage('Failed to load sections', 'error')
      }
    }

    const createSection = async () => {
      if (!newSectionName.value.trim()) return

      try {
        await sectionsAPI.create(newSectionName.value, newSectionIsGa.value)
        showMessage(`Section "${newSectionName.value}" created`, 'success')
        newSectionName.value = ''
        newSectionIsGa.value = false
        await loadSections()
      } catch (err) {
        showMessage('Failed to create section', 'error')
      }
    }

    const deleteSection = async (name) => {
      if (!confirm(`Delete section "${name}"?`)) return

      try {
        await sectionsAPI.delete(name)
        showMessage(`Section deleted`, 'success')
        await loadSections()
      } catch (err) {
        showMessage('Failed to delete section', 'error')
      }
    }

    const showRenameForm = (name) => {
      renamingSection.value = name
      newName.value = name
    }

    const renameSection = async () => {
      try {
        await sectionsAPI.rename(renamingSection.value, newName.value)
        showMessage(`Section renamed`, 'success')
        renamingSection.value = null
        await loadSections()
      } catch (err) {
        showMessage('Failed to rename section', 'error')
      }
    }

    const cloneSection = async (name) => {
      try {
        await sectionsAPI.clone(name, 1)
        showMessage(`Section cloned`, 'success')
        await loadSections()
      } catch (err) {
        showMessage('Failed to clone section', 'error')
      }
    }

    const deleteRow = async (sectionName, rowName) => {
      if (!confirm(`Delete row "${rowName}"?`)) return

      try {
        await sectionsAPI.deleteRow(sectionName, rowName)
        showMessage(`Row deleted`, 'success')
        await loadSections()
      } catch (err) {
        showMessage('Failed to delete row', 'error')
      }
    }

    const totalSeats = (section) => {
      return section.rows.reduce((sum, row) => sum + row.seats.length, 0)
    }

    const showMessage = (text, type = 'success') => {
      message.value = { text, type }
      setTimeout(() => (message.value = null), 3000)
    }

    onMounted(loadSections)

    return {
      sections,
      newSectionName,
      newSectionIsGa,
      renamingSection,
      newName,
      message,
      createSection,
      deleteSection,
      showRenameForm,
      renameSection,
      cloneSection,
      deleteRow,
      totalSeats,
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

.form-group {
  display: flex;
  gap: 1rem;
  flex-wrap: wrap;
  align-items: center;
}

.input {
  flex: 1;
  min-width: 200px;
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

.checkbox {
  display: flex;
  align-items: center;
  gap: 0.5rem;
  cursor: pointer;
}

.checkbox input {
  cursor: pointer;
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

.btn-success {
  background: #48bb78;
  color: white;
}

.btn-success:hover {
  background: #38a169;
}

.btn-danger {
  background: #f56565;
  color: white;
}

.btn-danger:hover {
  background: #e53e3e;
}

.btn-sm {
  padding: 0.5rem 1rem;
  font-size: 0.9rem;
  background: #e0e0e0;
  color: #333;
}

.btn-sm:hover {
  background: #d0d0d0;
}

.btn-xs {
  padding: 0.3rem 0.6rem;
  font-size: 0.8rem;
}

.sections-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(300px, 1fr));
  gap: 1.5rem;
}

.section-card {
  border: 1px solid #e0e0e0;
  border-radius: 8px;
  padding: 1.5rem;
  background: #fafafa;
}

.section-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 1rem;
}

.section-header h4 {
  margin: 0;
  color: #333;
}

.badge-ga {
  background: #ffd700;
  color: #333;
  padding: 0.25rem 0.75rem;
  border-radius: 12px;
  font-size: 0.8rem;
  font-weight: 600;
}

.section-stats {
  display: flex;
  gap: 1rem;
  margin-bottom: 1rem;
  font-size: 0.9rem;
  color: #666;
}

.section-actions {
  display: flex;
  gap: 0.5rem;
  margin-bottom: 1rem;
}

.section-actions .btn {
  flex: 1;
}

.rename-form {
  display: flex;
  gap: 0.5rem;
  margin-top: 1rem;
  padding-top: 1rem;
  border-top: 1px solid #ddd;
}

.input-sm {
  flex: 1;
  padding: 0.5rem;
  border: 1px solid #ddd;
  border-radius: 4px;
}

.rows-detail {
  margin-top: 1rem;
  cursor: pointer;
}

.rows-detail summary {
  color: #667eea;
  font-weight: 500;
  padding: 0.5rem 0;
}

.rows-list {
  margin-top: 1rem;
  padding-top: 1rem;
  border-top: 1px solid #ddd;
}

.row-item {
  padding: 0.75rem;
  background: white;
  border-radius: 4px;
  margin-bottom: 0.5rem;
  display: flex;
  justify-content: space-between;
  align-items: center;
  font-size: 0.9rem;
}

.empty-state {
  color: #999;
  text-align: center;
  padding: 2rem;
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
