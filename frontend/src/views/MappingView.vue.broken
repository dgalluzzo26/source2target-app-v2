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
            <Button
              icon="pi pi-cloud-download"
              label="Discover from Databricks"
              @click="showDiscoveryDialog = true"
              severity="info"
            />
            <Button
              icon="pi pi-link"
              label="Test Connection"
              @click="testConnection"
              :loading="loading.connection"
              severity="help"
            />
          </div>
        </div>

        <DataTable 
          :value="sourceTables" 
          :loading="loading.tables"
          paginator 
          :rows="10"
          :totalRecords="tablesPagination.total"
          lazy
          @page="onTablePage"
          dataKey="id"
          stripedRows
          showGridlines
        >
          <Column field="full_table_name" header="Table Name" sortable>
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
            <Dropdown 
              v-model="mappingFilters.status" 
              :options="statusOptions" 
              placeholder="Filter by Status"
              showClear
              @change="loadFieldMappings"
            />
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
          :totalRecords="mappingsPagination.total"
          lazy
          @page="onMappingPage"
          dataKey="id"
          stripedRows
          showGridlines
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
                  :disabled="data.is_validated"
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

      <!-- AI Suggestions Tab -->
      <TabPanel header="AI Suggestions">
        <div class="table-controls">
          <div class="search-controls">
            <IconField iconPosition="left">
              <InputIcon class="pi pi-search" />
              <InputText 
                v-model="suggestionSearch" 
                placeholder="Search suggestions..."
                @input="searchSuggestions"
              />
            </IconField>
            <Button 
              icon="pi pi-refresh" 
              @click="loadAISuggestions"
              :loading="loading.suggestions"
              severity="secondary"
            />
          </div>
        </div>

        <DataTable 
          :value="aiSuggestions" 
          :loading="loading.suggestions"
          paginator 
          :rows="10"
          dataKey="id"
          stripedRows
          showGridlines
        >
          <Column field="source_column_name" header="Source Column" sortable>
            <template #body="{ data }">
              <div class="column-info">
                <strong>{{ data.source_column_name }}</strong>
                <small>{{ data.source_table_name }}</small>
              </div>
            </template>
          </Column>
          
          <Column field="target_field_name" header="Suggested Target" sortable>
            <template #body="{ data }">
              <div class="column-info">
                <strong>{{ data.target_field_name }}</strong>
                <small>{{ data.target_schema_name }}</small>
              </div>
            </template>
          </Column>
          
          <Column field="confidence_score" header="Confidence" sortable>
            <template #body="{ data }">
              <div class="confidence-score">
                <ProgressBar :value="data.confidence_score * 100" :showValue="false" />
                <span>{{ Math.round(data.confidence_score * 100) }}%</span>
              </div>
            </template>
          </Column>
          
          <Column field="model_name" header="Model" sortable />
          
          <Column field="reasoning" header="Reasoning">
            <template #body="{ data }">
              <div class="reasoning-text">
                {{ data.reasoning.substring(0, 100) }}...
              </div>
            </template>
          </Column>
          
          <Column header="Actions">
            <template #body="{ data }">
              <div class="action-buttons">
                <Button 
                  icon="pi pi-check" 
                  size="small" 
                  severity="success"
                  @click="acceptSuggestion(data.id)"
                  v-tooltip="'Accept Suggestion'"
                />
                <Button 
                  icon="pi pi-times" 
                  size="small" 
                  severity="danger"
                  @click="rejectSuggestion(data.id)"
                  v-tooltip="'Reject Suggestion'"
                />
              </div>
            </template>
          </Column>
        </DataTable>
      </TabPanel>
    </TabView>

    <!-- Discovery Dialog -->
    <Dialog 
      v-model:visible="showDiscoveryDialog" 
      modal 
      header="Discover Tables from Databricks"
      :style="{ width: '50rem' }"
    >
      <div class="discovery-form">
        <div class="field">
          <label for="catalogs">Catalogs (comma-separated, leave empty for all):</label>
          <InputText 
            id="catalogs"
            v-model="discoveryForm.catalogs" 
            placeholder="e.g., catalog1, catalog2"
            class="w-full"
          />
        </div>
        
        <div class="field">
          <label for="search">Search Term (optional):</label>
          <InputText 
            id="search"
            v-model="discoveryForm.search" 
            placeholder="Search for specific table names"
            class="w-full"
          />
        </div>

        <div class="discovery-warning">
          <Message severity="warn" :closable="false">
            <strong>Note:</strong> Discovery may take several minutes for large catalogs. 
            This will scan Databricks Unity Catalog and sync table metadata to the platform.
          </Message>
        </div>
      </div>

      <template #footer>
        <Button 
          label="Cancel" 
          icon="pi pi-times" 
          @click="showDiscoveryDialog = false" 
          severity="secondary"
        />
        <Button 
          label="Start Discovery" 
          icon="pi pi-cloud-download" 
          @click="startDiscovery" 
          :loading="loading.discovery"
          severity="info"
        />
      </template>
    </Dialog>

    <!-- Discovery Results Dialog -->
    <Dialog 
      v-model:visible="showDiscoveryResults" 
      modal 
      header="Discovery Results"
      :style="{ width: '40rem' }"
    >
      <div class="discovery-results" v-if="discoveryResults">
        <div class="results-summary">
          <h4>Discovery Completed Successfully!</h4>
          <div class="stats-grid">
            <div class="stat-item">
              <span class="stat-label">Tables Found:</span>
              <span class="stat-value">{{ discoveryResults.stats.tables_discovered || 0 }}</span>
            </div>
            <div class="stat-item">
              <span class="stat-label">Tables Created:</span>
              <span class="stat-value">{{ discoveryResults.stats.tables_created || 0 }}</span>
            </div>
            <div class="stat-item">
              <span class="stat-label">Tables Updated:</span>
              <span class="stat-value">{{ discoveryResults.stats.tables_updated || 0 }}</span>
            </div>
            <div class="stat-item">
              <span class="stat-label">Columns Created:</span>
              <span class="stat-value">{{ discoveryResults.stats.columns_created || 0 }}</span>
            </div>
          </div>
        </div>

        <div v-if="discoveryResults.stats.errors && discoveryResults.stats.errors.length > 0" class="errors-section">
          <h5>Errors Encountered:</h5>
          <ul class="error-list">
            <li v-for="error in discoveryResults.stats.errors" :key="error">{{ error }}</li>
          </ul>
        </div>
      </div>

      <template #footer>
        <Button 
          label="Close" 
          icon="pi pi-check" 
          @click="closeDiscoveryResults" 
          severity="success"
        />
      </template>
    </Dialog>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted } from 'vue'
import { MappingAPI, handleApiError } from '@/services/api'

// Reactive data
const stats = ref<any>(null)
const sourceTables = ref<any[]>([])
const fieldMappings = ref<any[]>([])
const aiSuggestions = ref<any[]>([])

// Loading states
const loading = ref({
  stats: false,
  tables: false,
  mappings: false,
  suggestions: false,
  discovery: false,
  connection: false
})

// Search and filters
const tableSearch = ref('')
const mappingSearch = ref('')
const suggestionSearch = ref('')
const mappingFilters = ref({
  status: null
})

// Pagination
const tablesPagination = ref({ page: 1, total: 0 })
const mappingsPagination = ref({ page: 1, total: 0 })

// Options
const statusOptions = [
  { label: 'Draft', value: 'draft' },
  { label: 'Pending Review', value: 'pending_review' },
  { label: 'Approved', value: 'approved' },
  { label: 'Rejected', value: 'rejected' }
]

// Discovery dialog state
const showDiscoveryDialog = ref(false)
const showDiscoveryResults = ref(false)
const discoveryForm = ref({
  catalogs: '',
  search: ''
})
const discoveryResults = ref<any>(null)

// Methods
const loadMappingStats = async () => {
  loading.value.stats = true
  try {
    stats.value = await MappingAPI.getMappingStats()
  } catch (error) {
    console.error('Failed to load mapping stats:', error)
  } finally {
    loading.value.stats = false
  }
}

const loadSourceTables = async (page = 1) => {
  loading.value.tables = true
  try {
    const params = {
      page,
      search: tableSearch.value || undefined
    }
    const response = await MappingAPI.getSourceTables(params)
    sourceTables.value = response.results || response
    tablesPagination.value.total = response.count || response.length
  } catch (error) {
    console.error('Failed to load source tables:', error)
  } finally {
    loading.value.tables = false
  }
}

const loadFieldMappings = async (page = 1) => {
  loading.value.mappings = true
  try {
    const params = {
      page,
      search: mappingSearch.value || undefined,
      status: mappingFilters.value.status || undefined
    }
    const response = await MappingAPI.getFieldMappings(params)
    fieldMappings.value = response.results || response
    mappingsPagination.value.total = response.count || response.length
  } catch (error) {
    console.error('Failed to load field mappings:', error)
  } finally {
    loading.value.mappings = false
  }
}

const loadAISuggestions = async () => {
  loading.value.suggestions = true
  try {
    const params = {
      search: suggestionSearch.value || undefined
    }
    const response = await MappingAPI.getAISuggestions(params)
    aiSuggestions.value = response.results || response
  } catch (error) {
    console.error('Failed to load AI suggestions:', error)
  } finally {
    loading.value.suggestions = false
  }
}

// Event handlers
const onTablePage = (event: any) => {
  loadSourceTables(event.page + 1)
}

const onMappingPage = (event: any) => {
  loadFieldMappings(event.page + 1)
}

const searchTables = () => {
  loadSourceTables(1)
}

const searchMappings = () => {
  loadFieldMappings(1)
}

const searchSuggestions = () => {
  loadAISuggestions()
}

const viewTableDetails = (table: any) => {
  // TODO: Navigate to table details view
  console.log('View table details:', table)
}

const analyzeTable = async (tableId: number) => {
  try {
    await MappingAPI.analyzeTable(tableId)
    loadSourceTables()
  } catch (error) {
    console.error('Failed to analyze table:', error)
  }
}

const validateMapping = async (mappingId: number) => {
  try {
    await MappingAPI.validateMapping(mappingId)
    loadFieldMappings()
  } catch (error) {
    console.error('Failed to validate mapping:', error)
  }
}

const editMapping = (mapping: any) => {
  // TODO: Open edit mapping dialog
  console.log('Edit mapping:', mapping)
}

const acceptSuggestion = async (suggestionId: number) => {
  try {
    await MappingAPI.acceptAISuggestion(suggestionId)
    loadAISuggestions()
    loadFieldMappings()
    loadMappingStats()
  } catch (error) {
    console.error('Failed to accept suggestion:', error)
  }
}

const rejectSuggestion = async (suggestionId: number) => {
  try {
    await MappingAPI.rejectAISuggestion(suggestionId)
    loadAISuggestions()
  } catch (error) {
    console.error('Failed to reject suggestion:', error)
  }
}

const testConnection = async () => {
  loading.value.connection = true
  try {
    const result = await MappingAPI.testDatabricksConnection()
    // Show success message
    console.log('Connection test successful:', result)
    // You could add a toast notification here
  } catch (error) {
    console.error('Connection test failed:', error)
    // You could add an error toast notification here
  } finally {
    loading.value.connection = false
  }
}

const startDiscovery = async () => {
  loading.value.discovery = true
  try {
    const params: any = {}
    if (discoveryForm.value.catalogs.trim()) {
      params.catalogs = discoveryForm.value.catalogs.trim()
    }
    if (discoveryForm.value.search.trim()) {
      params.search = discoveryForm.value.search.trim()
    }

    const result = await MappingAPI.discoverTables(params)
    discoveryResults.value = result
    showDiscoveryDialog.value = false
    showDiscoveryResults.value = true
    
    // Reload tables to show newly discovered ones
    loadSourceTables()
    loadMappingStats()
    
  } catch (error) {
    console.error('Discovery failed:', error)
    // You could add an error toast notification here
  } finally {
    loading.value.discovery = false
  }
}

const closeDiscoveryResults = () => {
  showDiscoveryResults.value = false
  discoveryResults.value = null
  // Reset discovery form
  discoveryForm.value = {
    catalogs: '',
    search: ''
  }
}

// Utility functions
const getTableTypeSeverity = (type: string) => {
  const severityMap: Record<string, string> = {
    'TABLE': 'info',
    'VIEW': 'success',
    'EXTERNAL': 'warning',
    'TEMPORARY': 'secondary'
  }
  return severityMap[type] || 'info'
}

const getAnalysisStatusSeverity = (status: string) => {
  const severityMap: Record<string, string> = {
    'completed': 'success',
    'analyzing': 'info',
    'pending': 'warning',
    'failed': 'danger'
  }
  return severityMap[status] || 'secondary'
}

const getMappingTypeSeverity = (type: string) => {
  const severityMap: Record<string, string> = {
    'direct': 'success',
    'transformed': 'info',
    'calculated': 'warning',
    'lookup': 'secondary',
    'conditional': 'contrast'
  }
  return severityMap[type] || 'info'
}

const getStatusSeverity = (status: string) => {
  const severityMap: Record<string, string> = {
    'approved': 'success',
    'pending_review': 'warning',
    'draft': 'info',
    'rejected': 'danger',
    'archived': 'secondary'
  }
  return severityMap[status] || 'info'
}

// Initialize data
onMounted(() => {
  loadMappingStats()
  loadSourceTables()
  loadFieldMappings()
  loadAISuggestions()
})
</script>

<style scoped>
.discovery-form {
  display: flex;
  flex-direction: column;
  gap: 1rem;
}

.field {
  display: flex;
  flex-direction: column;
  gap: 0.5rem;
}

.field label {
  font-weight: 600;
  color: var(--p-text-color);
}

.discovery-warning {
  margin-top: 1rem;
}

.discovery-results {
  display: flex;
  flex-direction: column;
  gap: 1.5rem;
}

.results-summary h4 {
  color: var(--p-green-500);
  margin-bottom: 1rem;
}

.stats-grid {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 1rem;
}

.stat-item {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 0.75rem;
  background: var(--p-surface-100);
  border-radius: var(--p-border-radius);
  border-left: 4px solid var(--p-primary-color);
}

.stat-label {
  font-weight: 500;
  color: var(--p-text-muted-color);
}

.stat-value {
  font-weight: 700;
  font-size: 1.2rem;
  color: var(--p-primary-color);
}

.errors-section {
  margin-top: 1rem;
}

.errors-section h5 {
  color: var(--p-red-500);
  margin-bottom: 0.5rem;
}

.error-list {
  list-style-type: none;
  padding: 0;
}

.error-list li {
  padding: 0.5rem;
  background: var(--p-red-50);
  border-left: 4px solid var(--p-red-500);
  margin-bottom: 0.5rem;
  border-radius: var(--p-border-radius);
  color: var(--p-red-700);
}</style>
.mapping-view {
  max-width: 1400px;
  margin: 0 auto;
  display: flex;
  flex-direction: column;
  gap: 2rem;
}

.page-header {
  margin-bottom: 1rem;
}

.page-header h1 {
  display: flex;
  align-items: center;
  gap: 0.75rem;
  margin: 0 0 0.5rem 0;
  color: var(--p-text-color);
  font-size: 2rem;
}

.page-header p {
  margin: 0;
  color: var(--p-text-muted-color);
  font-size: 1.125rem;
}

/* Statistics Grid */
.stats-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
  gap: 1rem;
  margin-bottom: 1rem;
}

.stat-card {
  border: 1px solid var(--p-surface-border);
  transition: all 0.3s ease;
}

.stat-card:hover {
  transform: translateY(-2px);
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.1);
}

.stat-content {
  display: flex;
  flex-direction: column;
  align-items: center;
  text-align: center;
  position: relative;
  padding: 1rem;
}

.stat-value {
  font-size: 2rem;
  font-weight: 700;
  color: var(--p-primary-color);
  margin-bottom: 0.5rem;
}

.stat-label {
  font-size: 0.875rem;
  color: var(--p-text-muted-color);
  font-weight: 500;
}

.stat-icon {
  position: absolute;
  top: 1rem;
  right: 1rem;
  font-size: 1.5rem;
  color: var(--p-primary-color);
  opacity: 0.3;
}

/* Table Controls */
.table-controls {
  margin-bottom: 1rem;
}

.search-controls {
  display: flex;
  gap: 1rem;
  align-items: center;
  flex-wrap: wrap;
}

.search-controls .p-inputtext {
  min-width: 250px;
}

/* Table Styling */
.table-name {
  display: flex;
  flex-direction: column;
  gap: 0.25rem;
}

.table-name strong {
  color: var(--p-text-color);
}

.table-name small {
  color: var(--p-text-muted-color);
  font-size: 0.75rem;
}

.column-info {
  display: flex;
  flex-direction: column;
  gap: 0.25rem;
}

.column-info strong {
  color: var(--p-text-color);
}

.column-info small {
  color: var(--p-text-muted-color);
  font-size: 0.75rem;
}

.progress-container {
  display: flex;
  align-items: center;
  gap: 0.5rem;
}

.progress-container .p-progressbar {
  flex: 1;
  min-width: 60px;
}

.progress-text {
  font-size: 0.875rem;
  font-weight: 500;
  color: var(--p-text-color);
  min-width: 35px;
}

.confidence-score {
  display: flex;
  align-items: center;
  gap: 0.5rem;
}

.confidence-score .p-progressbar {
  flex: 1;
  min-width: 60px;
}

.confidence-score span {
  font-size: 0.875rem;
  font-weight: 500;
  color: var(--p-text-color);
  min-width: 35px;
}

.reasoning-text {
  max-width: 200px;
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
  color: var(--p-text-muted-color);
  font-size: 0.875rem;
}

.action-buttons {
  display: flex;
  gap: 0.5rem;
}

/* Responsive Design */
@media (max-width: 768px) {
  .mapping-view {
    max-width: 100%;
    padding: 0 1rem;
  }
  
  .stats-grid {
    grid-template-columns: repeat(2, 1fr);
  }
  
  .search-controls {
    flex-direction: column;
    align-items: stretch;
  }
  
  .search-controls .p-inputtext {
    min-width: auto;
  }
  
  .page-header h1 {
    font-size: 1.5rem;
  }
}

@media (max-width: 480px) {
  .stats-grid {
    grid-template-columns: 1fr;
  }
}
}

.page-header {
  margin-bottom: 2rem;
}

.page-header h1 {
  display: flex;
  align-items: center;
  gap: 0.75rem;
  margin: 0 0 0.5rem 0;
  color: var(--p-text-color);
  font-size: 2rem;
}

.page-header p {
  margin: 0;
  color: var(--p-text-muted-color);
  font-size: 1.125rem;
}

.coming-soon {
  text-align: center;
  padding: 3rem 2rem;
}

.coming-soon h2 {
  margin: 0 0 1rem 0;
  color: var(--p-text-color);
}

.coming-soon p {
  margin: 0 0 1.5rem 0;
  color: var(--p-text-muted-color);
  font-size: 1.125rem;
}

.coming-soon ul {
  text-align: left;
  max-width: 400px;
  margin: 0 auto;
  color: var(--p-text-muted-color);
}

.coming-soon li {
  margin-bottom: 0.5rem;
}
</style>

