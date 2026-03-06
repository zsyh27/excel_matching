/**
 * ConfigMigration - Utility for migrating legacy configuration data to new format
 * 
 * This utility handles:
 * 1. Splitting intelligent_cleaning into 4 separate sections
 * 2. Merging technical_terms into synonym_map with type field
 * 3. Detecting legacy format configurations
 * 4. Migrating complete configuration objects
 */

class ConfigMigration {
  /**
   * Detect if configuration is in legacy format
   * @param {Object} config - Configuration object to check
   * @returns {boolean} - True if legacy format detected
   */
  static detectLegacyFormat(config) {
    if (!config || typeof config !== 'object') {
      return false
    }

    // Check for legacy intelligent_cleaning field
    const hasIntelligentCleaning = 'intelligent_cleaning' in config || 'intelligent_extraction' in config
    
    // Check for legacy technical_terms field (separate from synonym_map)
    const hasSeparateTechnicalTerms = 'technical_terms' in config
    
    return hasIntelligentCleaning || hasSeparateTechnicalTerms
  }

  /**
   * Migrate intelligent_cleaning data to 4 separate sections
   * @param {Object} legacyData - Legacy intelligent_cleaning configuration
   * @returns {Object} - Migrated data with 4 sections
   */
  static migrateIntelligentCleaning(legacyData) {
    if (!legacyData || typeof legacyData !== 'object') {
      return {
        text_cleaning: {
          noise_patterns: [],
          metadata_rules: [],
          separator_mappings: []
        },
        normalization_map: [],
        feature_extraction: {
          separator_processing: [],
          param_decompose: [],
          smart_split: [],
          unit_remove: []
        },
        feature_quality: {
          quality_scoring: [],
          whitelist: []
        }
      }
    }

    // Extract text cleaning data
    const text_cleaning = {
      noise_patterns: legacyData.noise_patterns || legacyData.noise_filter || [],
      metadata_rules: legacyData.metadata_rules || legacyData.metadata_processing || [],
      separator_mappings: legacyData.separator_mappings || legacyData.separator_unify || []
    }

    // Extract normalization mapping (character-level replacements)
    const normalization_map = legacyData.normalization_map || legacyData.char_replacements || []

    // Extract feature extraction data
    const feature_extraction = {
      separator_processing: legacyData.separator_processing || legacyData.separator_process || [],
      param_decompose: legacyData.param_decompose || legacyData.parameter_decomposition || [],
      smart_split: legacyData.smart_split || legacyData.intelligent_split || [],
      unit_remove: legacyData.unit_remove || legacyData.unit_removal || []
    }

    // Extract feature quality data
    const feature_quality = {
      quality_scoring: legacyData.quality_scoring || legacyData.quality_rules || [],
      whitelist: legacyData.whitelist || legacyData.feature_whitelist || []
    }

    return {
      text_cleaning,
      normalization_map,
      feature_extraction,
      feature_quality
    }
  }

  /**
   * Migrate technical_terms to synonym_map format with type field
   * @param {Array} legacyTerms - Legacy technical terms array
   * @returns {Array} - Migrated mapping entries with type='technical'
   */
  static migrateTechnicalTerms(legacyTerms) {
    if (!Array.isArray(legacyTerms)) {
      return []
    }

    return legacyTerms.map((term, index) => {
      // Handle different legacy formats
      if (typeof term === 'object' && term !== null) {
        return {
          id: term.id || `tech_${index}`,
          source: term.source || term.from || term.abbreviation || '',
          target: term.target || term.to || term.expansion || '',
          type: 'technical',
          enabled: term.enabled !== undefined ? term.enabled : true
        }
      } else if (typeof term === 'string') {
        // Handle simple string format "abbr->expansion"
        const parts = term.split('->').map(s => s.trim())
        return {
          id: `tech_${index}`,
          source: parts[0] || '',
          target: parts[1] || '',
          type: 'technical',
          enabled: true
        }
      }
      
      return null
    }).filter(entry => entry !== null && entry.source && entry.target)
  }

  /**
   * Migrate complete configuration object from legacy to new format
   * @param {Object} legacyConfig - Legacy configuration object
   * @returns {Object} - Migrated configuration object
   */
  static migrateConfiguration(legacyConfig) {
    if (!legacyConfig || typeof legacyConfig !== 'object') {
      console.warn('ConfigMigration: Invalid configuration object provided')
      return legacyConfig
    }

    // Check if migration is needed
    if (!this.detectLegacyFormat(legacyConfig)) {
      console.log('ConfigMigration: Configuration is already in new format')
      return legacyConfig
    }

    console.log('ConfigMigration: Migrating configuration from legacy format')
    
    // Create a copy to avoid mutating original
    const migratedConfig = { ...legacyConfig }

    // Migrate intelligent_cleaning if present
    if (legacyConfig.intelligent_cleaning || legacyConfig.intelligent_extraction) {
      const cleaningData = legacyConfig.intelligent_cleaning || legacyConfig.intelligent_extraction
      const migrated = this.migrateIntelligentCleaning(cleaningData)
      
      // Add migrated sections to config
      migratedConfig.text_cleaning = migrated.text_cleaning
      migratedConfig.normalization_map = migrated.normalization_map
      migratedConfig.feature_extraction = migrated.feature_extraction
      migratedConfig.feature_quality = migrated.feature_quality
      
      // Remove legacy field
      delete migratedConfig.intelligent_cleaning
      delete migratedConfig.intelligent_extraction
    }

    // Migrate technical_terms if present
    if (legacyConfig.technical_terms) {
      const migratedTerms = this.migrateTechnicalTerms(legacyConfig.technical_terms)
      
      // Merge with existing synonym_map
      const existingSynonyms = Array.isArray(migratedConfig.synonym_map) 
        ? migratedConfig.synonym_map 
        : []
      
      // Add type='synonym' to existing synonyms if not present
      const typedSynonyms = existingSynonyms.map(entry => ({
        ...entry,
        type: entry.type || 'synonym'
      }))
      
      // Combine technical terms and synonyms
      migratedConfig.synonym_map = [...typedSynonyms, ...migratedTerms]
      
      // Remove legacy field
      delete migratedConfig.technical_terms
    }

    // Ensure all synonym_map entries have type field
    if (Array.isArray(migratedConfig.synonym_map)) {
      migratedConfig.synonym_map = migratedConfig.synonym_map.map(entry => ({
        ...entry,
        type: entry.type || 'synonym'
      }))
    }

    console.log('ConfigMigration: Migration completed successfully')
    return migratedConfig
  }

  /**
   * Map new format back to legacy format for backward compatibility
   * @param {Object} newConfig - Configuration in new format
   * @returns {Object} - Configuration in legacy format
   */
  static mapNewToLegacyFormat(newConfig) {
    if (!newConfig || typeof newConfig !== 'object') {
      return newConfig
    }

    const legacyConfig = { ...newConfig }

    // Reconstruct intelligent_cleaning from 4 sections
    if (newConfig.text_cleaning || newConfig.normalization_map || 
        newConfig.feature_extraction || newConfig.feature_quality) {
      
      legacyConfig.intelligent_extraction = {
        noise_patterns: newConfig.text_cleaning?.noise_patterns || [],
        metadata_rules: newConfig.text_cleaning?.metadata_rules || [],
        separator_mappings: newConfig.text_cleaning?.separator_mappings || [],
        normalization_map: newConfig.normalization_map || [],
        separator_processing: newConfig.feature_extraction?.separator_processing || [],
        param_decompose: newConfig.feature_extraction?.param_decompose || [],
        smart_split: newConfig.feature_extraction?.smart_split || [],
        unit_remove: newConfig.feature_extraction?.unit_remove || [],
        quality_scoring: newConfig.feature_quality?.quality_scoring || [],
        whitelist: newConfig.feature_quality?.whitelist || []
      }
      
      // Remove new format fields
      delete legacyConfig.text_cleaning
      delete legacyConfig.normalization_map
      delete legacyConfig.feature_extraction
      delete legacyConfig.feature_quality
    }

    // Extract technical_terms from synonym_map
    if (Array.isArray(newConfig.synonym_map)) {
      const technicalTerms = newConfig.synonym_map
        .filter(entry => entry.type === 'technical')
        .map(({ type, ...rest }) => rest)
      
      const synonyms = newConfig.synonym_map
        .filter(entry => entry.type !== 'technical')
        .map(({ type, ...rest }) => rest)
      
      if (technicalTerms.length > 0) {
        legacyConfig.technical_terms = technicalTerms
      }
      
      legacyConfig.synonym_map = synonyms
    }

    return legacyConfig
  }
}

export default ConfigMigration
