<template>
  <div id="app">
    <header class="header">
      <h1>🎭 Seating Plan Manager</h1>
      <div class="project-info">
        <span v-if="currentProjectName" class="badge">{{ currentProjectName }}</span>
      </div>
    </header>

    <nav class="nav">
      <button
        v-for="tab in tabs"
        :key="tab"
        :class="['nav-btn', { active: activeTab === tab }]"
        @click="activeTab = tab"
      >
        {{ tab }}
      </button>
    </nav>

    <main class="container">
      <ProjectManager
        v-show="activeTab === 'Projects'"
        @project-created="onProjectCreated"
        @project-loaded="onProjectLoaded"
      />

      <SectionManager
        v-show="activeTab === 'Sections'"
        :key="currentProjectName"
      />

      <SeatManager
        v-show="activeTab === 'Seats'"
        :key="currentProjectName"
      />
    </main>
  </div>
</template>

<script>
import { ref } from 'vue'
import ProjectManager from './components/ProjectManager.vue'
import SectionManager from './components/SectionManager.vue'
import SeatManager from './components/SeatManager.vue'

export default {
  name: 'App',
  components: {
    ProjectManager,
    SectionManager,
    SeatManager,
  },
  setup() {
    const activeTab = ref('Projects')
    const currentProjectName = ref('')
    const tabs = ['Projects', 'Sections', 'Seats']

    const onProjectCreated = (name) => {
      currentProjectName.value = name
      activeTab.value = 'Sections'
    }

    const onProjectLoaded = (name) => {
      currentProjectName.value = name
      activeTab.value = 'Sections'
    }

    return {
      activeTab,
      currentProjectName,
      tabs,
      onProjectCreated,
      onProjectLoaded,
    }
  },
}
</script>

<style scoped>
#app {
  font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, 'Helvetica Neue', Arial, sans-serif;
  background: #f5f5f5;
  min-height: 100vh;
}

.header {
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  color: white;
  padding: 2rem;
  box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.header h1 {
  margin: 0;
  font-size: 2rem;
}

.project-info {
  display: flex;
  gap: 1rem;
}

.badge {
  background: rgba(255, 255, 255, 0.3);
  padding: 0.5rem 1rem;
  border-radius: 20px;
  font-size: 0.9rem;
  font-weight: 500;
}

.nav {
  display: flex;
  gap: 0;
  background: white;
  border-bottom: 2px solid #e0e0e0;
  padding: 0 2rem;
}

.nav-btn {
  padding: 1rem 1.5rem;
  border: none;
  background: none;
  cursor: pointer;
  font-size: 1rem;
  font-weight: 500;
  color: #666;
  border-bottom: 3px solid transparent;
  transition: all 0.3s ease;
}

.nav-btn:hover {
  color: #667eea;
}

.nav-btn.active {
  color: #667eea;
  border-bottom-color: #667eea;
}

.container {
  max-width: 1200px;
  margin: 2rem auto;
  padding: 0 2rem;
}
</style>
