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
              @click="discoverTables"
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
          :value="filteredSourceTables" 
          :loading="loading.tables"
          paginator 
          :rows="10"
          :rowsPerPageOptions="[5, 10, 20, 50]"
          tableStyle="min-width: 50rem"
          rowHover
          class="p-datatable-sm"
        >
          <Column field="table_name" header="Source Table" sortable>
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
                <Button 
                  icon="pi pi-magic-wand" 
                  size="small" 
                  severity="success"
                  @click="generateAIMappings(data)"
                  v-tooltip="'Generate AI Mappings'"
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
            <Button 
              icon="pi pi-plus" 
              label="Create Mapping"
              @click="createMapping"
              severity="primary"
            />
            <Button 
              icon="pi pi-upload" 
              label="Upload Template"
              @click="uploadTemplate"
              severity="info"
            />
          </div>
        </div>

        <DataTable 
          :value="filteredFieldMappings" 
          :loading="loading.mappings"
          paginator 
          :rows="10"
          :rowsPerPageOptions="[5, 10, 20, 50]"
          tableStyle="min-width: 50rem"
          rowHover
          class="p-datatable-sm"
          selectionMode="single"
          v-model:selection="selectedMapping"
          @rowSelect="onMappingSelect"
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
              <i class="pi pi-arrow-right" style="color: var(--gainwell-secondary);"></i>
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
                <Button 
                  icon="pi pi-trash" 
                  size="small" 
                  severity="danger"
                  @click="deleteMapping(data.id)"
                  v-tooltip="'Delete Mapping'"
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
                v-model="aiSearch"
                placeholder="Search AI suggestions..."
                @input="searchAISuggestions"
              />
            </IconField>
            <Button 
              icon="pi pi-refresh" 
              @click="loadAISuggestions"
              :loading="loading.suggestions"
              severity="secondary"
            />
            <Button 
              icon="pi pi-magic-wand" 
              label="Generate New Suggestions"
              @click="generateAISuggestions"
              :loading="loading.generating"
              severity="primary"
            />
          </div>
        </div>

        <DataTable 
          :value="filteredAISuggestions" 
          :loading="loading.suggestions"
          paginator 
          :rows="10"
          :rowsPerPageOptions="[5, 10, 20, 50]"
          tableStyle="min-width: 50rem"
          rowHover
          class="p-datatable-sm"
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
          
          <Column field="target_field_name" header="Suggested Target" sortable>
            <template #body="{ data }">
              <div class="column-info">
                <strong>{{ data.target_field_name }}</strong>
                <small>{{ data.target_schema_name }}</small>
                <Tag :value="data.target_data_type" size="small" />
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
                <Button 
                  icon="pi pi-eye" 
                  size="small" 
                  severity="info"
                  @click="viewSuggestionDetails(data)"
                  v-tooltip="'View Details'"
                />
              </div>
            </template>
          </Column>
        </DataTable>
      </TabPanel>
    </TabView>

    <!-- Mapping Detail Dialog -->
    <Dialog 
      v-model:visible="showMappingDetail" 
      modal 
      header="Mapping Details"
      :style="{ width: '60rem' }"
    >
      <div v-if="selectedMapping" class="mapping-detail">
        <div class="detail-grid">
          <div class="detail-section">
            <h4>Source Information</h4>
            <div class="detail-item">
              <label>Table:</label>
              <span>{{ selectedMapping.source_table_name }}</span>
            </div>
            <div class="detail-item">
              <label>Column:</label>
              <span>{{ selectedMapping.source_column_name }}</span>
            </div>
            <div class="detail-item">
              <label>Data Type:</label>
              <Tag :value="selectedMapping.source_data_type" />
            </div>
          </div>

          <div class="detail-section">
            <h4>Target Information</h4>
            <div class="detail-item">
              <label>Schema:</label>
              <span>{{ selectedMapping.target_schema_name }}</span>
            </div>
            <div class="detail-item">
              <label>Field:</label>
              <span>{{ selectedMapping.target_field_name }}</span>
            </div>
            <div class="detail-item">
              <label>Data Type:</label>
              <Tag :value="selectedMapping.target_data_type" />
            </div>
          </div>
        </div>

        <div class="mapping-metadata">
          <div class="metadata-item">
            <label>Mapping Type:</label>
            <Tag :value="selectedMapping.mapping_type" :severity="getMappingTypeSeverity(selectedMapping.mapping_type)" />
          </div>
          <div class="metadata-item" v-if="selectedMapping.confidence_score">
            <label>Confidence Score:</label>
            <div class="confidence-score">
              <ProgressBar :value="selectedMapping.confidence_score * 100" :showValue="false" />
              <span>{{ Math.round(selectedMapping.confidence_score * 100) }}%</span>
            </div>
          </div>
          <div class="metadata-item">
            <label>Status:</label>
            <Tag 
              :value="selectedMapping.status" 
              :severity="getStatusSeverity(selectedMapping.status)"
              :icon="selectedMapping.is_validated ? 'pi pi-check' : undefined"
            />
          </div>
        </div>

        <div v-if="selectedMapping.validation_notes" class="validation-notes">
          <h4>Validation Notes</h4>
          <p>{{ selectedMapping.validation_notes }}</p>
        </div>
      </div>

      <template #footer>
        <Button 
          label="Close" 
          icon="pi pi-times" 
          @click="showMappingDetail = false" 
          severity="secondary"
        />
        <Button 
          v-if="selectedMapping && !selectedMapping.is_validated"
          label="Validate" 
          icon="pi pi-check" 
          @click="validateMapping(selectedMapping.id)" 
          severity="success"
        />
        <Button 
          label="Edit" 
          icon="pi pi-pencil" 
          @click="editMapping(selectedMapping)" 
          severity="info"
        />
      </template>
    </Dialog>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted, computed } from 'vue'
import { MappingAPI, handleApiError } from '@/services/api'

// Reactive data with comprehensive dummy data
const stats = ref({
  total_tables: 47,
  total_columns: 1234,
  mapped_columns: 892,
  mapping_progress: 72
})

const sourceTables = ref([
  {
    id: 1,
    table_name: 'patient_demographics',
    catalog_name: 'healthcare_raw',
    schema_name: 'patient_data',
    table_type: 'MANAGED',
    column_count: 15,
    mapping_progress: 87,
    analysis_status: 'analyzed'
  },
  {
    id: 2,
    table_name: 'claims_summary',
    catalog_name: 'healthcare_raw',
    schema_name: 'claims_data',
    table_type: 'EXTERNAL',
    column_count: 28,
    mapping_progress: 64,
    analysis_status: 'analyzed'
  },
  {
    id: 3,
    table_name: 'provider_network',
    catalog_name: 'healthcare_raw',
    schema_name: 'provider_data',
    table_type: 'VIEW',
    column_count: 22,
    mapping_progress: 91,
    analysis_status: 'analyzed'
  },
  {
    id: 4,
    table_name: 'medication_history',
    catalog_name: 'healthcare_raw',
    schema_name: 'pharmacy_data',
    table_type: 'MANAGED',
    column_count: 19,
    mapping_progress: 43,
    analysis_status: 'pending'
  },
  {
    id: 5,
    table_name: 'enrollment_periods',
    catalog_name: 'healthcare_raw',
    schema_name: 'member_data',
    table_type: 'MANAGED',
    column_count: 12,
    mapping_progress: 100,
    analysis_status: 'analyzed'
  }
])

const fieldMappings = ref([
  {
    id: 1,
    source_column_name: 'patient_id',
    source_table_name: 'patient_demographics',
    source_data_type: 'STRING',
    target_field_name: 'member_id',
    target_schema_name: 'unified_member',
    target_data_type: 'VARCHAR(50)',
    mapping_type: 'MANUAL',
    confidence_score: null,
    status: 'VALIDATED',
    is_validated: true,
    validation_notes: 'Direct mapping confirmed by business analyst'
  },
  {
    id: 2,
    source_column_name: 'first_name',
    source_table_name: 'patient_demographics',
    source_data_type: 'STRING',
    target_field_name: 'member_first_name',
    target_schema_name: 'unified_member',
    target_data_type: 'VARCHAR(100)',
    mapping_type: 'AI_SUGGESTION',
    confidence_score: 0.95,
    status: 'VALIDATED',
    is_validated: true,
    validation_notes: 'High confidence AI mapping, validated by SME'
  },
  {
    id: 3,
    source_column_name: 'date_of_birth',
    source_table_name: 'patient_demographics',
    source_data_type: 'DATE',
    target_field_name: 'member_birth_date',
    target_schema_name: 'unified_member',
    target_data_type: 'DATE',
    mapping_type: 'TEMPLATE',
    confidence_score: null,
    status: 'VALIDATED',
    is_validated: true,
    validation_notes: 'Standard demographic mapping from template'
  },
  {
    id: 4,
    source_column_name: 'claim_amount',
    source_table_name: 'claims_summary',
    source_data_type: 'DECIMAL(10,2)',
    target_field_name: 'total_claim_amount',
    target_schema_name: 'unified_claims',
    target_data_type: 'DECIMAL(12,2)',
    mapping_type: 'AI_SUGGESTION',
    confidence_score: 0.88,
    status: 'PENDING',
    is_validated: false,
    validation_notes: null
  },
  {
    id: 5,
    source_column_name: 'provider_npi',
    source_table_name: 'provider_network',
    source_data_type: 'STRING',
    target_field_name: 'provider_national_id',
    target_schema_name: 'unified_provider',
    target_data_type: 'VARCHAR(10)',
    mapping_type: 'MANUAL',
    confidence_score: null,
    status: 'REJECTED',
    is_validated: false,
    validation_notes: 'Rejected due to data quality issues in source'
  }
])

const aiSuggestions = ref([
  {
    id: 1,
    source_column_name: 'member_ssn',
    source_table_name: 'enrollment_periods',
    source_data_type: 'STRING',
    target_field_name: 'member_social_security',
    target_schema_name: 'unified_member',
    target_data_type: 'VARCHAR(11)',
    confidence_score: 0.92,
    model_name: 'llama-3-70b',
    reasoning: 'Strong semantic match between SSN fields. Both represent social security numbers for member identification. Data types are compatible with proper formatting.',
    status: 'PENDING'
  },
  {
    id: 2,
    source_column_name: 'drug_ndc',
    source_table_name: 'medication_history',
    source_data_type: 'STRING',
    target_field_name: 'medication_ndc_code',
    target_schema_name: 'unified_pharmacy',
    target_data_type: 'VARCHAR(11)',
    confidence_score: 0.89,
    model_name: 'llama-3-70b',
    reasoning: 'NDC (National Drug Code) is a standard identifier for medications. High confidence match based on field naming and healthcare domain context.',
    status: 'PENDING'
  },
  {
    id: 3,
    source_column_name: 'service_date',
    source_table_name: 'claims_summary',
    source_data_type: 'DATE',
    target_field_name: 'claim_service_date',
    target_schema_name: 'unified_claims',
    target_data_type: 'DATE',
    confidence_score: 0.94,
    model_name: 'llama-3-70b',
    reasoning: 'Direct semantic match for service dates in claims processing. Both fields represent when healthcare services were provided.',
    status: 'PENDING'
  }
])

// Search and filter states
const tableSearch = ref('')
const mappingSearch = ref('')
const aiSearch = ref('')

// Dialog states
const showMappingDetail = ref(false)
const selectedMapping = ref(null)

// Loading states
const loading = ref({
  tables: false,
  mappings: false,
  suggestions: false,
  connection: false,
  generating: false
})

// Computed filtered data
const filteredSourceTables = computed(() => {
  if (!tableSearch.value) return sourceTables.value
  return sourceTables.value.filter(table => 
    table.table_name.toLowerCase().includes(tableSearch.value.toLowerCase()) ||
    table.catalog_name.toLowerCase().includes(tableSearch.value.toLowerCase()) ||
    table.schema_name.toLowerCase().includes(tableSearch.value.toLowerCase())
  )
})

const filteredFieldMappings = computed(() => {
  if (!mappingSearch.value) return fieldMappings.value
  return fieldMappings.value.filter(mapping => 
    mapping.source_column_name.toLowerCase().includes(mappingSearch.value.toLowerCase()) ||
    mapping.source_table_name.toLowerCase().includes(mappingSearch.value.toLowerCase()) ||
    mapping.target_field_name.toLowerCase().includes(mappingSearch.value.toLowerCase()) ||
    mapping.target_schema_name.toLowerCase().includes(mappingSearch.value.toLowerCase())
  )
})

const filteredAISuggestions = computed(() => {
  if (!aiSearch.value) return aiSuggestions.value
  return aiSuggestions.value.filter(suggestion => 
    suggestion.source_column_name.toLowerCase().includes(aiSearch.value.toLowerCase()) ||
    suggestion.source_table_name.toLowerCase().includes(aiSearch.value.toLowerCase()) ||
    suggestion.target_field_name.toLowerCase().includes(aiSearch.value.toLowerCase()) ||
    suggestion.reasoning.toLowerCase().includes(aiSearch.value.toLowerCase())
  )
})

// Methods
const loadSourceTables = async () => {
  loading.value.tables = true
  // Simulate API call
  setTimeout(() => {
    loading.value.tables = false
    console.log('Source tables loaded')
  }, 1000)
}

const loadFieldMappings = async () => {
  loading.value.mappings = true
  // Simulate API call
  setTimeout(() => {
    loading.value.mappings = false
    console.log('Field mappings loaded')
  }, 1000)
}

const loadAISuggestions = async () => {
  loading.value.suggestions = true
  // Simulate API call
  setTimeout(() => {
    loading.value.suggestions = false
    console.log('AI suggestions loaded')
  }, 1000)
}

const searchTables = () => {
  console.log('Searching tables:', tableSearch.value)
}

const searchMappings = () => {
  console.log('Searching mappings:', mappingSearch.value)
}

const searchAISuggestions = () => {
  console.log('Searching AI suggestions:', aiSearch.value)
}

const viewTableDetails = (table: any) => {
  console.log('View table details:', table)
}

const analyzeTable = (tableId: number) => {
  console.log('Analyze table:', tableId)
}

const generateAIMappings = (table: any) => {
  console.log('Generate AI mappings for table:', table)
}

const testConnection = () => {
  loading.value.connection = true
  setTimeout(() => {
    loading.value.connection = false
    console.log('Connection test completed')
  }, 2000)
}

const discoverTables = () => {
  console.log('Discover tables from Databricks')
}

const createMapping = () => {
  console.log('Create new mapping')
}

const uploadTemplate = () => {
  console.log('Upload mapping template')
}

const onMappingSelect = (event: any) => {
  selectedMapping.value = event.data
  showMappingDetail.value = true
}

const validateMapping = (mappingId: number) => {
  console.log('Validate mapping:', mappingId)
  const mapping = fieldMappings.value.find(m => m.id === mappingId)
  if (mapping) {
    mapping.is_validated = true
    mapping.status = 'VALIDATED'
  }
}

const editMapping = (mapping: any) => {
  console.log('Edit mapping:', mapping)
}

const deleteMapping = (mappingId: number) => {
  console.log('Delete mapping:', mappingId)
  const index = fieldMappings.value.findIndex(m => m.id === mappingId)
  if (index > -1) {
    fieldMappings.value.splice(index, 1)
  }
}

const generateAISuggestions = () => {
  loading.value.generating = true
  setTimeout(() => {
    loading.value.generating = false
    console.log('AI suggestions generated')
  }, 3000)
}

const acceptSuggestion = (suggestionId: number) => {
  console.log('Accept AI suggestion:', suggestionId)
  const suggestion = aiSuggestions.value.find(s => s.id === suggestionId)
  if (suggestion) {
    // Convert suggestion to mapping
    const newMapping = {
      id: fieldMappings.value.length + 1,
      source_column_name: suggestion.source_column_name,
      source_table_name: suggestion.source_table_name,
      source_data_type: suggestion.source_data_type,
      target_field_name: suggestion.target_field_name,
      target_schema_name: suggestion.target_schema_name,
      target_data_type: suggestion.target_data_type,
      mapping_type: 'AI_SUGGESTION',
      confidence_score: suggestion.confidence_score,
      status: 'PENDING',
      is_validated: false,
      validation_notes: null
    }
    fieldMappings.value.push(newMapping)
    
    // Remove from suggestions
    const index = aiSuggestions.value.findIndex(s => s.id === suggestionId)
    if (index > -1) {
      aiSuggestions.value.splice(index, 1)
    }
  }
}

const rejectSuggestion = (suggestionId: number) => {
  console.log('Reject AI suggestion:', suggestionId)
  const index = aiSuggestions.value.findIndex(s => s.id === suggestionId)
  if (index > -1) {
    aiSuggestions.value.splice(index, 1)
  }
}

const viewSuggestionDetails = (suggestion: any) => {
  console.log('View suggestion details:', suggestion)
}

// Utility methods for styling
const getTableTypeSeverity = (type: string) => {
  switch (type) {
    case 'MANAGED': return 'success'
    case 'EXTERNAL': return 'info'
    case 'VIEW': return 'warning'
    default: return 'secondary'
  }
}

const getAnalysisStatusSeverity = (status: string) => {
  switch (status) {
    case 'analyzed': return 'success'
    case 'pending': return 'info'
    case 'failed': return 'danger'
    default: return 'secondary'
  }
}

const getMappingTypeSeverity = (type: string) => {
  switch (type) {
    case 'AI_SUGGESTION': return 'info'
    case 'MANUAL': return 'secondary'
    case 'TEMPLATE': return 'success'
    default: return 'secondary'
  }
}

const getStatusSeverity = (status: string) => {
  switch (status) {
    case 'VALIDATED': return 'success'
    case 'PENDING': return 'info'
    case 'REJECTED': return 'danger'
    default: return 'secondary'
  }
}

onMounted(() => {
  console.log('Mapping view with dummy data loaded')
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

/* Statistics Grid */
.stats-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(250px, 1fr));
  gap: 1.5rem;
  margin-bottom: 2rem;
}

.stat-card {
  text-align: center;
  background: var(--gainwell-bg-primary);
  border: 1px solid var(--gainwell-border);
  border-radius: var(--p-border-radius);
  box-shadow: var(--p-card-shadow);
  transition: all 0.3s ease;
}

.stat-card:hover {
  transform: translateY(-3px);
  box-shadow: 0 6px 16px rgba(0, 0, 0, 0.1);
}

.stat-content {
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 0.5rem;
  position: relative;
  padding: 1.5rem;
}

.stat-value {
  font-size: 2.5rem;
  font-weight: 700;
  color: var(--gainwell-primary);
  line-height: 1;
}

.stat-label {
  color: var(--gainwell-text-secondary);
  font-weight: 500;
}

.stat-icon {
  position: absolute;
  top: 1rem;
  right: 1rem;
  font-size: 2.5rem;
  color: var(--gainwell-bg-secondary);
  opacity: 0.6;
}

/* Table Controls */
.table-controls {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 1.5rem;
  padding: 1rem;
  background: var(--gainwell-bg-light);
  border-radius: 8px;
}

.search-controls {
  display: flex;
  gap: 0.75rem;
  align-items: center;
  flex-wrap: wrap;
}

/* Table Styling */
.table-name {
  display: flex;
  flex-direction: column;
  gap: 0.25rem;
}

.table-name strong, .column-info strong {
  color: var(--gainwell-primary);
}

.table-name small, .column-info small {
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

.action-buttons {
  display: flex;
  gap: 0.5rem;
}

.reasoning-text {
  max-width: 250px;
  white-space: normal;
  word-wrap: break-word;
  font-size: 0.875rem;
  color: var(--gainwell-text-secondary);
}

/* Dialog Styling */
.mapping-detail {
  display: flex;
  flex-direction: column;
  gap: 1.5rem;
}

.detail-grid {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 2rem;
}

.detail-section h4 {
  color: var(--gainwell-primary);
  margin-bottom: 1rem;
}

.detail-item {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 0.5rem 0;
  border-bottom: 1px solid var(--gainwell-border);
}

.detail-item label {
  font-weight: 600;
  color: var(--gainwell-text-primary);
}

.mapping-metadata {
  display: flex;
  gap: 2rem;
  flex-wrap: wrap;
}

.metadata-item {
  display: flex;
  flex-direction: column;
  gap: 0.5rem;
}

.metadata-item label {
  font-weight: 600;
  color: var(--gainwell-text-primary);
}

.validation-notes h4 {
  color: var(--gainwell-primary);
  margin-bottom: 0.5rem;
}

.validation-notes p {
  color: var(--gainwell-text-secondary);
  line-height: 1.5;
}
</style>
