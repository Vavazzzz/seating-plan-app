<template>
  <div class="panel">
    <h2>Project Manager</h2>

    <div class="section">
      <h3>Create New Project</h3>
      <div class="form-group">
        <input
          v-model="newProjectName"
          type="text"
          placeholder="Enter project name"
          @keyup.enter="createProject"
          class="input"
        />
        <button @click="createProject" class="btn btn-primary">Create</button>
      </div>
    </div>

    <div class="section">
      <h3>Load Project</h3>
      <div v-if="projects.length" class="project-list">
        <div v-for="project in projects" :key="project" class="project-item">
          <span>{{ project }}</span>
          <div class="btn-group">
            <button @click="loadProject(project)" class="btn btn-secondary">Load</button>
            <button @click="deleteProject(project)" class="btn btn-danger">Delete</button>
          </div>
        </div>
      </div>
      <p v-else class="empty-state">No projects saved yet</p>
    </div>

    <div class="section">
      <h3>Save Current Project</h3>
      <div class="form-group">
        <input
          v-model="saveAsName"
          type="text"
          placeholder="Save as name"
          @keyup.enter="saveProject"
          class="input"
        />
        <button @click="saveProject" class="btn btn-success">Save</button>
      </div>
    </div>

    <div v-if="message" :class="['message', message.type]">
      {{ message.text }}
    </div>
  </div>
</template>

<script>
import { ref, onMounted } from 'vue'
import { projectsAPI } from '../api'

export default {
  name: 'ProjectManager',
  emits: ['project-created', 'project-loaded'],
  setup(props, { emit }) {
    const newProjectName = ref('')
    const saveAsName = ref('')
    const projects = ref([])
    const message = ref(null)

    const loadProjects = async () => {
      try {
        const res = await projectsAPI.list()
        projects.value = res.data.projects || []
      } catch (err) {
        showMessage('Failed to load projects', 'error')
      }
    }

    const createProject = async () => {
      if (!newProjectName.value.trim()) return

      try {
        await projectsAPI.new(newProjectName.value)
        showMessage(`Project "${newProjectName.value}" created`, 'success')
        emit('project-created', newProjectName.value)
        newProjectName.value = ''
      } catch (err) {
        showMessage('Failed to create project', 'error')
      }
    }

    const saveProject = async () => {
      if (!saveAsName.value.trim()) return

      try {
        await projectsAPI.save(saveAsName.value)
        showMessage(`Project saved as "${saveAsName.value}"`, 'success')
        await loadProjects()
        saveAsName.value = ''
      } catch (err) {
        showMessage('Failed to save project', 'error')
      }
    }

    const loadProject = async (name) => {
      try {
        await projectsAPI.load(name)
        showMessage(`Loaded project "${name}"`, 'success')
        emit('project-loaded', name)
      } catch (err) {
        showMessage('Failed to load project', 'error')
      }
    }

    const deleteProject = async (name) => {
      if (!confirm(`Delete project "${name}"?`)) return

      try {
        await projectsAPI.delete(name)
        showMessage(`Project "${name}" deleted`, 'success')
        await loadProjects()
      } catch (err) {
        showMessage('Failed to delete project', 'error')
      }
    }

    const showMessage = (text, type = 'success') => {
      message.value = { text, type }
      setTimeout(() => (message.value = null), 3000)
    }

    onMounted(loadProjects)

    return {
      newProjectName,
      saveAsName,
      projects,
      message,
      createProject,
      saveProject,
      loadProject,
      deleteProject,
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
}

.input {
  flex: 1;
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

.btn-danger {
  background: #f56565;
  color: white;
}

.btn-danger:hover {
  background: #e53e3e;
}

.project-list {
  display: flex;
  flex-direction: column;
  gap: 0.75rem;
}

.project-item {
  padding: 1rem;
  background: #f9f9f9;
  border-radius: 4px;
  display: flex;
  justify-content: space-between;
  align-items: center;
  border-left: 4px solid #667eea;
}

.btn-group {
  display: flex;
  gap: 0.5rem;
}

.btn-group button {
  padding: 0.5rem 1rem;
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
