# Design Document: Configuration Menu Restructure

## Overview

This design restructures the configuration management menu in a device matching system from a flat, feature-based organization to a hierarchical, workflow-based organization. The restructuring merges duplicate functionality (technical term expansion + synonym mapping), splits the monolithic intelligent cleaning feature into 4 logical sub-sections, and implements 2-level menu hierarchy support.

The key design principle is to organize configurations by their position in the device matching workflow: Pre-entry → Import → Preprocessing → Matching → Global. This makes it intuitive for administrators to find and configure each processing stage.

## Architecture

### Component Structure

```
ConfigManagementView.vue (Main Container)
├── MenuNavigation Component (New)
│   ├── WorkflowStageGroup Component (New)
│   │   ├── MenuItem Component (Enhanced)
│   │   └── SubMenuItem Component (New)
│   └── MenuStateManager (New)
├── ConfigEditorContainer Component (Enhanced)
│   ├── SynonymMapEditor (Enhanced - merged with technical terms)
│   ├── TextCleaningEditor (New - split from intelligent cleaning)
│   ├── NormalizationEditor (Existing)
│   ├── FeatureExtractionEditor (New - split from intelligent cleaning)
│   ├── FeatureQualityEditor (New - split from intelligent cleaning)
│   └── [Other existing editors...]
└── ConfigDataService (Enhanced)
    ├── Migration utilities
    └── Backward compatibility layer
```

### Data Flow

1. User clicks menu item → MenuNavigation emits selection event
2. ConfigManagementView receives event → Updates active editor
3. ConfigEditorContainer loads appropriate editor component
4. Editor loads configuration via ConfigDataService
5. ConfigDataService checks for legacy data format → Migrates if needed
6. Editor displays configuration → User makes changes
7. User saves → ConfigDataService validates and persists
8. Backend API receives save request → Updates database
9. TextPreprocessor/MatchEngine use updated configuration

### Workflow Stages

The menu is organized into 5 workflow stages that mirror the code execution flow:

1. **Pre-entry Configuration** (before data entry)
   - Brand Keywords
   - Device Parameters
   - Feature Weights

2. **Data Import Stage** (during data import)
   - Device Row Recognition

3. **Preprocessing Configuration** (TextPreprocessor.preprocess())
   - Text Cleaning (noise, metadata, separators)
   - Normalization Mapping (character replacements)
   - Feature Extraction (separator processing, decomposition, splitting, units)
   - Feature Quality (scoring, whitelist)

4. **Matching Configuration** (MatchEngine.match())
   - Synonym Mapping (merged: synonyms + technical terms)
   - Device Type Keywords
   - Match Threshold

5. **Global Configuration** (system-wide)
   - Global Settings

## Components and Interfaces

### MenuNavigation Component (New)

Renders the hierarchical menu structure with workflow stages.

```typescript
interface MenuNavigation {
  props: {
    menuStructure: WorkflowStage[]
    activeItemId: string
  }
  
  emits: {
    'menu-item-selected': (itemId: string) => void
  }
  
  data: {
    expandedStages: Set<string>
    expandedSubMenus: Set<string>
  }
  
  methods: {
    toggleStage(stageId: string): void
    toggleSubMenu(subMenuId: string): void
    selectMenuItem(itemId: string): void
    isActive(itemId: string): boolean
    isExpanded(id: string): boolean
  }
}

interface WorkflowStage {
  id: string
  name: string
  icon: string
  items: MenuItem[]
}

interface MenuItem {
  id: string
  name: string
  component?: string  // Editor component name
  subItems?: SubMenuItem[]
}

interface SubMenuItem {
  id: string
  name: string
  component: string  // Editor component name
}
```

### MenuStateManager (New)

Manages menu expansion state and active selection persistence.

```typescript
interface MenuStateManager {
  saveState(state: MenuState): void
  loadState(): MenuState | null
  getDefaultState(): MenuState
}

interface MenuState {
  activeItemId: string
  expandedStages: string[]
  expandedSubMenus: string[]
}
```

### ConfigEditorContainer Component (Enhanced)

Dynamically loads the appropriate configuration editor based on menu selection.

```typescript
interface ConfigEditorContainer {
  props: {
    activeEditorComponent: string
    editorProps: Record<string, any>
  }
  
  computed: {
    currentEditor: Component
  }
  
  methods: {
    loadEditor(componentName: string): Component
  }
}
```

### SynonymMapEditor Component (Enhanced)

Unified interface for both synonym mappings and technical term expansions.

```typescript
interface SynonymMapEditor {
  data: {
    mappings: MappingEntry[]
    filterType: 'all' | 'synonym' | 'technical'
  }
  
  methods: {
    addMapping(entry: MappingEntry): void
    editMapping(id: string, entry: MappingEntry): void
    deleteMapping(id: string): void
    filterByType(type: string): void
    saveMappings(): Promise<void>
    loadMappings(): Promise<void>
  }
}

interface MappingEntry {
  id: string
  source: string
  target: string
  type: 'synonym' | 'technical'  // New field
  enabled: boolean
}
```

### TextCleaningEditor Component (New)

Manages noise filtering, metadata processing, and separator unification configurations.

```typescript
interface TextCleaningEditor {
  data: {
    noisePatterns: string[]
    metadataRules: MetadataRule[]
    separatorMappings: SeparatorMapping[]
  }
  
  methods: {
    addNoisePattern(pattern: string): void
    addMetadataRule(rule: MetadataRule): void
    addSeparatorMapping(mapping: SeparatorMapping): void
    saveConfiguration(): Promise<void>
    loadConfiguration(): Promise<void>
  }
}

interface MetadataRule {
  pattern: string
  action: 'remove' | 'extract' | 'replace'
  replacement?: string
}

interface SeparatorMapping {
  from: string
  to: string
}
```

### FeatureExtractionEditor Component (New)

Manages separator processing, parameter decomposition, smart splitting, and unit removal.

```typescript
interface FeatureExtractionEditor {
  data: {
    separatorConfig: SeparatorConfig
    decompositionRules: DecompositionRule[]
    splittingRules: SplittingRule[]
    unitPatterns: string[]
  }
  
  methods: {
    configureSeparators(config: SeparatorConfig): void
    addDecompositionRule(rule: DecompositionRule): void
    addSplittingRule(rule: SplittingRule): void
    addUnitPattern(pattern: string): void
    saveConfiguration(): Promise<void>
    loadConfiguration(): Promise<void>
  }
}

interface SeparatorConfig {
  enabled: boolean
  separators: string[]
}

interface DecompositionRule {
  pattern: string
  extractionLogic: string
}

interface SplittingRule {
  condition: string
  splitLogic: string
}
```

### FeatureQualityEditor Component (New)

Manages quality scoring and whitelist configurations.

```typescript
interface FeatureQualityEditor {
  data: {
    scoringRules: ScoringRule[]
    whitelist: WhitelistEntry[]
  }
  
  methods: {
    addScoringRule(rule: ScoringRule): void
    addWhitelistEntry(entry: WhitelistEntry): void
    saveConfiguration(): Promise<void>
    loadConfiguration(): Promise<void>
  }
}

interface ScoringRule {
  criterion: string
  weight: number
  threshold: number
}

interface WhitelistEntry {
  value: string
  category: string
}
```

### ConfigDataService (Enhanced)

Handles configuration persistence with migration and backward compatibility.

```typescript
interface ConfigDataService {
  // Core operations
  loadConfig(configType: string): Promise<any>
  saveConfig(configType: string, data: any): Promise<void>
  
  // Migration
  migrateIntelligentCleaning(legacyData: any): MigratedCleaningData
  migrateTechnicalTerms(legacyData: any): MappingEntry[]
  
  // Backward compatibility
  mapNewToLegacyFormat(configType: string, data: any): any
  mapLegacyToNewFormat(configType: string, data: any): any
}

interface MigratedCleaningData {
  textCleaning: any
  normalization: any
  featureExtraction: any
  featureQuality: any
}
```

## Data Models

### Menu Structure Definition

The menu structure is defined as a static configuration that drives the MenuNavigation component:

```typescript
const MENU_STRUCTURE: WorkflowStage[] = [
  {
    id: 'pre-entry',
    name: '📝 设备信息录入前配置',
    items: [
      { id: 'brand-keywords', name: '品牌关键词', component: 'BrandKeywordEditor' },
      { id: 'device-params', name: '设备参数配置', component: 'DeviceParamEditor' },
      { id: 'feature-weights', name: '特征权重', component: 'FeatureWeightEditor' }
    ]
  },
  {
    id: 'import',
    name: '📥 数据导入阶段',
    items: [
      { id: 'device-row', name: '设备行识别', component: 'DeviceRowEditor' }
    ]
  },
  {
    id: 'preprocessing',
    name: '🔍 预处理配置',
    items: [
      {
        id: 'text-cleaning',
        name: '文本清理',
        subItems: [
          { id: 'noise-filter', name: '噪音过滤', component: 'NoiseFilterEditor' },
          { id: 'metadata', name: '元数据处理', component: 'MetadataEditor' },
          { id: 'separator-unify', name: '分隔符统一', component: 'SeparatorUnifyEditor' }
        ]
      },
      {
        id: 'normalization',
        name: '归一化映射',
        component: 'NormalizationEditor'
      },
      {
        id: 'feature-extraction',
        name: '特征提取',
        subItems: [
          { id: 'separator-process', name: '处理分隔符', component: 'SeparatorProcessEditor' },
          { id: 'param-decompose', name: '复杂参数分解', component: 'ParamDecomposeEditor' },
          { id: 'smart-split', name: '智能拆分', component: 'SmartSplitEditor' },
          { id: 'unit-remove', name: '单位删除', component: 'UnitRemoveEditor' }
        ]
      },
      {
        id: 'feature-quality',
        name: '特征质量',
        subItems: [
          { id: 'quality-score', name: '质量评分', component: 'QualityScoreEditor' },
          { id: 'whitelist', name: '白名单', component: 'WhitelistEditor' }
        ]
      }
    ]
  },
  {
    id: 'matching',
    name: '🎯 匹配配置阶段',
    items: [
      { id: 'synonym-map', name: '同义词映射', component: 'SynonymMapEditor' },
      { id: 'device-type', name: '设备类型关键词', component: 'DeviceTypeEditor' },
      { id: 'match-threshold', name: '匹配阈值', component: 'MatchThresholdEditor' }
    ]
  },
  {
    id: 'global',
    name: '⚙️ 全局配置',
    items: [
      { id: 'global-settings', name: '全局配置', component: 'GlobalSettingsEditor' }
    ]
  }
]
```

### Configuration Storage Schema

Configurations are stored in the database with the following schema changes:

**Before (Legacy):**
```json
{
  "intelligent_cleaning": {
    "noise_patterns": [...],
    "metadata_rules": [...],
    "separator_mappings": [...],
    "decomposition_rules": [...],
    "splitting_rules": [...],
    "unit_patterns": [...],
    "scoring_rules": [...],
    "whitelist": [...]
  },
  "technical_term_expansion": {
    "mappings": [...]
  },
  "synonym_mapping": {
    "mappings": [...]
  }
}
```

**After (New):**
```json
{
  "text_cleaning": {
    "noise_patterns": [...],
    "metadata_rules": [...],
    "separator_mappings": [...]
  },
  "normalization_mapping": {
    "character_replacements": [...]
  },
  "feature_extraction": {
    "separator_config": {...},
    "decomposition_rules": [...],
    "splitting_rules": [...],
    "unit_patterns": [...]
  },
  "feature_quality": {
    "scoring_rules": [...],
    "whitelist": [...]
  },
  "synonym_mapping": {
    "mappings": [
      {"source": "...", "target": "...", "type": "synonym"},
      {"source": "...", "target": "...", "type": "technical"}
    ]
  }
}
```

### Migration Strategy

The ConfigDataService implements a migration layer that:

1. Detects legacy configuration format on load
2. Transforms legacy data to new structure
3. Saves in new format on next save operation
4. Maintains backward compatibility for API consumers

```typescript
function migrateConfiguration(legacyConfig: any): any {
  const newConfig: any = {}
  
  // Split intelligent cleaning
  if (legacyConfig.intelligent_cleaning) {
    const ic = legacyConfig.intelligent_cleaning
    
    newConfig.text_cleaning = {
      noise_patterns: ic.noise_patterns || [],
      metadata_rules: ic.metadata_rules || [],
      separator_mappings: ic.separator_mappings || []
    }
    
    newConfig.feature_extraction = {
      separator_config: ic.separator_config || {},
      decomposition_rules: ic.decomposition_rules || [],
      splitting_rules: ic.splitting_rules || [],
      unit_patterns: ic.unit_patterns || []
    }
    
    newConfig.feature_quality = {
      scoring_rules: ic.scoring_rules || [],
      whitelist: ic.whitelist || []
    }
  }
  
  // Merge technical terms into synonym mapping
  if (legacyConfig.synonym_mapping || legacyConfig.technical_term_expansion) {
    const synonyms = (legacyConfig.synonym_mapping?.mappings || [])
      .map(m => ({ ...m, type: 'synonym' }))
    
    const technical = (legacyConfig.technical_term_expansion?.mappings || [])
      .map(m => ({ ...m, type: 'technical' }))
    
    newConfig.synonym_mapping = {
      mappings: [...synonyms, ...technical]
    }
  }
  
  // Copy other configs unchanged
  for (const key in legacyConfig) {
    if (!['intelligent_cleaning', 'technical_term_expansion', 'synonym_mapping'].includes(key)) {
      newConfig[key] = legacyConfig[key]
    }
  }
  
  return newConfig
}
```


## Correctness Properties

A property is a characteristic or behavior that should hold true across all valid executions of a system—essentially, a formal statement about what the system should do. Properties serve as the bridge between human-readable specifications and machine-verifiable correctness guarantees.

### Property 1: Menu item click behavior

*For any* menu item, clicking it should expand sub-items if they exist, or navigate to the configuration page if no sub-items exist.

**Validates: Requirements 2.2, 2.3**

### Property 2: Configuration data migration preserves all data

*For any* existing configuration database state (including intelligent cleaning data, technical term expansions, and synonym mappings), after running the migration process, all configuration values should be present in the new structure with correct type annotations and section mappings.

**Validates: Requirements 3.4, 3.5, 4.7, 5.1, 5.3**

### Property 3: Configuration round-trip consistency

*For any* valid configuration data, saving it and then loading it should return equivalent configuration values.

**Validates: Requirements 5.5, 6.1, 6.2**

### Property 4: API backward compatibility

*For any* existing API endpoint and valid request that worked before restructuring, the same request should still return a valid response after restructuring.

**Validates: Requirements 5.2, 6.5**

### Property 5: Configuration validation consistency

*For any* configuration data, if it was valid before restructuring, it should remain valid after restructuring, and if it was invalid before, it should remain invalid after.

**Validates: Requirements 6.3**

### Property 6: Matching behavior preservation

*For any* device matching input and configuration, the matching results should be identical before and after the menu restructuring.

**Validates: Requirements 6.4, 6.7**

### Property 7: Active menu item highlighting

*For any* menu item, when selected, it should have an active/highlighted visual state, and all other menu items should not be highlighted.

**Validates: Requirements 7.1**

### Property 8: Sub-menu expansion state persistence

*For any* sub-menu, after expanding it, it should remain expanded until explicitly collapsed by the user or the page is refreshed.

**Validates: Requirements 7.2**

### Property 9: Parent menu auto-expansion

*For any* sub-menu item, when navigated to directly (e.g., via URL or programmatic navigation), its parent menu should automatically expand to show the selected item.

**Validates: Requirements 7.3**

### Property 10: Menu state restoration after page refresh

*For any* menu selection and expansion state, after refreshing the page, the same menu item should be selected and the same sub-menus should be expanded.

**Validates: Requirements 7.4**

## Error Handling

### Menu Navigation Errors

**Invalid Menu Item Selection:**
- If a menu item ID doesn't exist in the menu structure, log an error and default to the first menu item
- Display a user-friendly message: "Configuration page not found"

**Editor Component Loading Failure:**
- If an editor component fails to load, display an error message in the ConfigEditorContainer
- Log the error with component name and stack trace
- Provide a "Retry" button to attempt reloading

**Menu State Corruption:**
- If saved menu state in localStorage is corrupted or invalid, clear it and use default state
- Log a warning about state reset

### Configuration Data Errors

**Migration Failure:**
- If migration encounters unexpected data format, log detailed error with data sample
- Fall back to treating data as new format
- Display warning to user: "Some configurations may need to be reconfigured"

**Save Operation Failure:**
- If save fails due to network error, display error message with retry option
- If save fails due to validation error, highlight invalid fields and show validation messages
- Preserve user's unsaved changes in component state

**Load Operation Failure:**
- If load fails due to network error, display error message with retry option
- If load fails due to missing data, initialize with empty/default configuration
- Log warning about missing configuration

**Data Validation Errors:**
- Validate all configuration data before saving
- Display field-level validation errors inline
- Prevent save operation until all validation errors are resolved

### API Compatibility Errors

**Legacy API Endpoint Failure:**
- If a legacy API endpoint is called but fails, log the error with endpoint and parameters
- Return appropriate HTTP error code (400 for bad request, 500 for server error)
- Include error message in response body

**Data Format Mismatch:**
- If API receives data in unexpected format, attempt to parse both legacy and new formats
- If parsing fails, return 400 error with details about expected format
- Log the mismatch for debugging

## Testing Strategy

This feature requires both unit tests and property-based tests to ensure comprehensive coverage.

### Unit Testing Approach

Unit tests will focus on specific examples, edge cases, and integration points:

**Menu Structure Tests:**
- Verify the MENU_STRUCTURE constant contains exactly 5 workflow stages
- Verify each stage has the correct icon and name
- Verify stages appear in the correct order
- Verify Preprocessing stage has 4 sub-sections with correct names
- Verify Text Cleaning has 3 sub-items, Feature Extraction has 4, Feature Quality has 2
- Verify "Intelligent Cleaning" menu item does not exist
- Verify "Synonym Mapping" exists under Matching Configuration stage

**Component Rendering Tests:**
- Test MenuNavigation renders all stages and items correctly
- Test ConfigEditorContainer loads correct editor component for each menu item
- Test SynonymMapEditor displays both synonym and technical term entries
- Test each new editor component (TextCleaningEditor, FeatureExtractionEditor, FeatureQualityEditor) renders correctly

**Migration Logic Tests:**
- Test migrateIntelligentCleaning() correctly splits data into 4 sections
- Test migrateTechnicalTerms() adds type='technical' to all entries
- Test migration handles missing fields gracefully
- Test migration handles empty data

**Error Handling Tests:**
- Test invalid menu item ID defaults to first item
- Test corrupted localStorage state resets to default
- Test editor component loading failure displays error message
- Test save failure preserves unsaved changes
- Test load failure initializes with defaults

### Property-Based Testing Approach

Property-based tests will verify universal properties across all inputs using a PBT library (fast-check for JavaScript/TypeScript). Each test will run a minimum of 100 iterations.

**Property Test 1: Menu item click behavior**
- Generate random menu items (with and without sub-items)
- Click each item
- Verify: items with sub-items expand, items without sub-items navigate
- Tag: **Feature: config-menu-restructure, Property 1: Menu item click behavior**

**Property Test 2: Configuration data migration preserves all data**
- Generate random configuration databases with various combinations of intelligent cleaning, technical terms, and synonyms
- Run migration on each
- Verify: all original data present in new structure, correct type annotations, correct section mappings
- Tag: **Feature: config-menu-restructure, Property 2: Configuration data migration preserves all data**

**Property Test 3: Configuration round-trip consistency**
- Generate random valid configurations
- Save each configuration
- Load each configuration
- Verify: loaded data equals saved data
- Tag: **Feature: config-menu-restructure, Property 3: Configuration round-trip consistency**

**Property Test 4: API backward compatibility**
- Generate random valid API requests that worked before restructuring
- Send each request to the API
- Verify: all requests return valid responses
- Tag: **Feature: config-menu-restructure, Property 4: API backward compatibility**

**Property Test 5: Configuration validation consistency**
- Generate random configurations (both valid and invalid)
- Check validation before and after restructuring
- Verify: validation results are identical
- Tag: **Feature: config-menu-restructure, Property 5: Configuration validation consistency**

**Property Test 6: Matching behavior preservation**
- Generate random device matching inputs and configurations
- Run matching before and after restructuring
- Verify: matching results are identical
- Tag: **Feature: config-menu-restructure, Property 6: Matching behavior preservation**

**Property Test 7: Active menu item highlighting**
- Generate random menu items
- Select each item
- Verify: selected item is highlighted, all others are not
- Tag: **Feature: config-menu-restructure, Property 7: Active menu item highlighting**

**Property Test 8: Sub-menu expansion state persistence**
- Generate random sub-menus
- Expand each sub-menu
- Verify: sub-menu remains expanded until explicitly collapsed
- Tag: **Feature: config-menu-restructure, Property 8: Sub-menu expansion state persistence**

**Property Test 9: Parent menu auto-expansion**
- Generate random sub-menu items
- Navigate to each item directly
- Verify: parent menu automatically expands
- Tag: **Feature: config-menu-restructure, Property 9: Parent menu auto-expansion**

**Property Test 10: Menu state restoration after page refresh**
- Generate random menu selections and expansion states
- Save state and simulate page refresh
- Verify: same menu item selected, same sub-menus expanded
- Tag: **Feature: config-menu-restructure, Property 10: Menu state restoration after page refresh**

### Testing Configuration

- **PBT Library:** fast-check (for JavaScript/TypeScript)
- **Minimum Iterations:** 100 per property test
- **Unit Test Framework:** Jest or Vitest (depending on project setup)
- **Component Testing:** Vue Test Utils for component rendering tests
- **API Testing:** Supertest or similar for API endpoint tests

### Test Data Generation

For property-based tests, we need generators for:

- **Menu items:** Generate items with/without sub-items, various IDs and names
- **Configuration data:** Generate valid intelligent cleaning configs, technical terms, synonyms
- **API requests:** Generate valid requests for all existing endpoints
- **Device matching inputs:** Generate device descriptions and configurations
- **Menu states:** Generate valid combinations of selected items and expanded sub-menus

### Integration Testing

Beyond unit and property tests, integration tests should verify:

- End-to-end workflow: User opens menu → selects item → edits configuration → saves → configuration is applied to matching
- Migration workflow: Existing database → migration runs → new menu loads → all data accessible
- Backward compatibility: Old API clients → make requests → receive valid responses
