<template>
  <div class="mapping-view">
    <div class="page-header">
      <h1>
        <i class="pi pi-sitemap"></i>
        Field Mapping
      </h1>
      <p>Map source fields to target schema with AI-powered suggestions</p>
    </div>

    <!-- Statistics Cards -->
    <div class="stats-grid" v-if="stats">
      <Card class="stat-card">
        <template #content>
          <div class="stat-content">
            <div class="stat-value">{{ stats.total_tables }}</div>
            <div class="stat-label">Source Tables</div>
            <i class="pi pi-table stat-icon"></i>
          </div>
        </template>
      </Card>
      
      <Card class="stat-card">
        <template #content>
          <div class="stat-content">
            <div class="stat-value">{{ stats.total_columns }}</div>
            <div class="stat-label">Total Columns</div>
            <i class="pi pi-list stat-icon"></i>
          </div>
        </template>
      </Card>
      
      <Card class="stat-card">
        <template #content>
          <div class="stat-content">
            <div class="stat-value">{{ stats.mapped_columns }}</div>
            <div class="stat-label">Mapped Columns</div>
            <i class="pi pi-check-circle stat-icon"></i>
          </div>
        </template>
      </Card>
      
      <Card class="stat-card">
        <template #content>
          <div class="stat-content">
            <div class="stat-value">{{ stats.mapping_progress }}%</div>
            <div class="stat-label">Progress</div>
            <i class="pi pi-chart-line stat-icon"></i>
          </div>
        </template>
      </Card>
    </div>

    <!-- Main Content Tabs -->
    <TabView>
      <!-- Source Tables Tab -->
      <TabPanel header="Source Tables">
        <div class="table-controls">
          <div class="search-controls">
            <IconField iconPosition="left">
              <InputIcon class="pi pi-search" />
              <InputText
                v-model="tableSearch"
                placeholder="Search tables..."
                @input="searchTables"
              />
            </IconField>
            <Button
              icon="pi pi-refresh"
              @click="loadSourceTables"
              :loading="loading.tables"
              severity="secondary"
            />
          </div>
        </div>

        <DataTable 
          :value="sourceTables" 
          :loading="loading.tables"
          paginator 
          :rows="10"
          :rowsPerPageOptions="[5, 10, 20, 50]"
          tableStyle="min-width: 50rem"
        >
          <Column field="table_name" header="Table Name" sortable>
            <template #body="{ data }">
              <div class="table-name">
                <strong>{{ data.table_name }}</strong>
                <small>{{ data.catalog_name }}.{{ data.schema_name }}</small>
              </div>
            </template>
          </Column>
          
          <Column field="table_type" header="Type" sortable>
            <template #body="{ data }">
              <Tag :value="data.table_type" :severity="getTableTypeSeverity(data.table_type)" />
            </template>
          </Column>
          
          <Column field="column_count" header="Columns" sortable />
          
          <Column field="mapping_progress" header="Progress" sortable>
            <template #body="{ data }">
              <div class="progress-container">
                <ProgressBar :value="data.mapping_progress" :showValue="false" />
                <span class="progress-text">{{ data.mapping_progress }}%</span>
              </div>
            </template>
          </Column>
          
          <Column field="analysis_status" header="Status" sortable>
            <template #body="{ data }">
              <Tag 
                :value="data.analysis_status" 
                :severity="getAnalysisStatusSeverity(data.analysis_status)" 
              />
            </template>
          </Column>
          
          <Column header="Actions">
            <template #body="{ data }">
              <div class="action-buttons">
                <Button 
                  icon="pi pi-eye" 
                  size="small" 
                  severity="info"
                  @click="viewTableDetails(data)"
                  v-tooltip="'View Details'"
                />
                <Button 
                  icon="pi pi-cog" 
                  size="small" 
                  severity="secondary"
                  @click="analyzeTable(data.id)"
                  v-tooltip="'Analyze Table'"
                />
              </div>
            </template>
          </Column>
        </DataTable>
      </TabPanel>

      <!-- Field Mappings Tab -->
      <TabPanel header="Field Mappings">
        <div class="table-controls">
          <div class="search-controls">
            <IconField iconPosition="left">
              <InputIcon class="pi pi-search" />
              <InputText
                v-model="mappingSearch"
                placeholder="Search mappings..."
                @input="searchMappings"
              />
            </IconField>
            <Button 
              icon="pi pi-refresh" 
              @click="loadFieldMappings"
              :loading="loading.mappings"
              severity="secondary"
            />
          </div>
        </div>

        <DataTable 
          :value="fieldMappings" 
          :loading="loading.mappings"
          paginator 
          :rows="10"
          :rowsPerPageOptions="[5, 10, 20, 50]"
          tableStyle="min-width: 50rem"
        >
          <Column field="source_column_name" header="Source Column" sortable>
            <template #body="{ data }">
              <div class="column-info">
                <strong>{{ data.source_column_name }}</strong>
                <small>{{ data.source_table_name }}</small>
                <Tag :value="data.source_data_type" size="small" />
              </div>
            </template>
          </Column>
          
          <Column header="→" style="width: 3rem; text-align: center;">
            <template #body>
              <i class="pi pi-arrow-right" style="color: var(--p-primary-color);"></i>
            </template>
          </Column>
          
          <Column field="target_field_name" header="Target Field" sortable>
            <template #body="{ data }">
              <div class="column-info">
                <strong>{{ data.target_field_name }}</strong>
                <small>{{ data.target_schema_name }}</small>
                <Tag :value="data.target_data_type" size="small" />
              </div>
            </template>
          </Column>
          
          <Column field="mapping_type" header="Type" sortable>
            <template #body="{ data }">
              <Tag :value="data.mapping_type" :severity="getMappingTypeSeverity(data.mapping_type)" />
            </template>
          </Column>
          
          <Column field="confidence_score" header="Confidence" sortable>
            <template #body="{ data }">
              <div v-if="data.confidence_score" class="confidence-score">
                <ProgressBar :value="data.confidence_score * 100" :showValue="false" />
                <span>{{ Math.round(data.confidence_score * 100) }}%</span>
              </div>
              <span v-else>-</span>
            </template>
          </Column>
          
          <Column field="status" header="Status" sortable>
            <template #body="{ data }">
              <Tag 
                :value="data.status" 
                :severity="getStatusSeverity(data.status)"
                :icon="data.is_validated ? 'pi pi-check' : undefined"
              />
            </template>
          </Column>
          
          <Column header="Actions">
            <template #body="{ data }">
              <div class="action-buttons">
                <Button 
                  icon="pi pi-check" 
                  size="small" 
                  severity="success"
                  @click="validateMapping(data.id)"
                  v-tooltip="'Validate Mapping'"
                />
                <Button 
                  icon="pi pi-pencil" 
                  size="small" 
                  severity="info"
                  @click="editMapping(data)"
                  v-tooltip="'Edit Mapping'"
                />
              </div>
            </template>
          </Column>
        </DataTable>
      </TabPanel>
    </TabView>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted } from 'vue'
import { MappingAPI, handleApiError } from '@/services/api'

// Reactive data
const stats = ref<any>(null)
const sourceTables = ref<any[]>([])
const fieldMappings = ref<any[]>([])
const tableSearch = ref('')
const mappingSearch = ref('')

// Loading states
const loading = ref({
  stats: false,
  tables: false,
  mappings: false
})

// Methods
const loadMappingStats = async () => {
  // Implementation
}

const loadSourceTables = async () => {
  // Implementation
}

const loadFieldMappings = async () => {
  // Implementation
}

const searchTables = () => {
  // Implementation
}

const searchMappings = () => {
  // Implementation
}

const viewTableDetails = (data: any) => {
  // Implementation
}

const analyzeTable = (id: number) => {
  // Implementation
}

const validateMapping = (id: number) => {
  // Implementation
}

const editMapping = (data: any) => {
  // Implementation
}

const getTableTypeSeverity = (type: string) => {
  return 'info'
}

const getAnalysisStatusSeverity = (status: string) => {
  return 'success'
}

const getMappingTypeSeverity = (type: string) => {
  return 'info'
}

const getStatusSeverity = (status: string) => {
  return 'success'
}

onMounted(() => {
  loadMappingStats()
  loadSourceTables()
  loadFieldMappings()
})
</script>

<style scoped>
.mapping-view {
  padding: 0;
}

.page-header {
  margin-bottom: 2rem;
}

.page-header h1 {
  display: flex;
  align-items: center;
  gap: 0.5rem;
  margin: 0 0 0.5rem 0;
  color: var(--gainwell-primary);
}

.stats-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(250px, 1fr));
  gap: 1.5rem;
  margin-bottom: 2rem;
}

.stat-card {
  text-align: center;
}

.stat-content {
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 0.5rem;
}

.stat-value {
  font-size: 2rem;
  font-weight: bold;
  color: var(--gainwell-primary);
}

.stat-label {
  color: var(--gainwell-text-secondary);
  font-weight: 500;
}

.stat-icon {
  font-size: 1.5rem;
  color: var(--gainwell-secondary);
}

.table-controls {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 1rem;
  padding: 1rem;
  background: var(--gainwell-bg-light);
  border-radius: 8px;
}

.search-controls {
  display: flex;
  gap: 1rem;
  align-items: center;
}

.action-buttons {
  display: flex;
  gap: 0.5rem;
}

.table-name {
  display: flex;
  flex-direction: column;
  gap: 0.25rem;
}

.table-name small {
  color: var(--gainwell-text-secondary);
  font-size: 0.8rem;
}

.column-info {
  display: flex;
  flex-direction: column;
  gap: 0.25rem;
}

.progress-container {
  display: flex;
  align-items: center;
  gap: 0.5rem;
}

.progress-text {
  font-size: 0.875rem;
  font-weight: 500;
}

.confidence-score {
  display: flex;
  align-items: center;
  gap: 0.5rem;
}
</style>
