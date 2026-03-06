/**
 * TypeScript definitions for ConfigMigration utility
 */

export interface MappingEntry {
  id: string
  source: string
  target: string
  type: 'synonym' | 'technical'
  enabled: boolean
}

export interface TextCleaningConfig {
  noise_patterns: string[]
  metadata_rules: any[]
  separator_mappings: any[]
}

export interface FeatureExtractionConfig {
  separator_processing: any[]
  param_decompose: any[]
  smart_split: any[]
  unit_remove: any[]
}

export interface FeatureQualityConfig {
  quality_scoring: any[]
  whitelist: any[]
}

export interface MigratedCleaningData {
  text_cleaning: TextCleaningConfig
  normalization_map: any[]
  feature_extraction: FeatureExtractionConfig
  feature_quality: FeatureQualityConfig
}

export default class ConfigMigration {
  /**
   * Detect if configuration is in legacy format
   */
  static detectLegacyFormat(config: any): boolean

  /**
   * Migrate intelligent_cleaning data to 4 separate sections
   */
  static migrateIntelligentCleaning(legacyData: any): MigratedCleaningData

  /**
   * Migrate technical_terms to synonym_map format with type field
   */
  static migrateTechnicalTerms(legacyTerms: any[]): MappingEntry[]

  /**
   * Migrate complete configuration object from legacy to new format
   */
  static migrateConfiguration(legacyConfig: any): any

  /**
   * Map new format back to legacy format for backward compatibility
   */
  static mapNewToLegacyFormat(newConfig: any): any
}
