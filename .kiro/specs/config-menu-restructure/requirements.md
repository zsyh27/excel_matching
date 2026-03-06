# Requirements Document

## Introduction

This document specifies the requirements for restructuring the configuration management menu in a device matching system. The current menu structure has overlapping functionality and poor organization. The restructuring will organize menu items by workflow stages, merge duplicate features, and implement hierarchical sub-menus for better usability.

## Glossary

- **ConfigManagementView**: The main Vue.js component that displays the configuration management interface
- **Menu_Item**: A clickable navigation element in the configuration menu
- **Sub_Menu**: A nested menu structure that appears under a parent menu item
- **Workflow_Stage**: A logical phase in the device matching process (pre-entry, import, preprocessing, matching, global)
- **Technical_Term_Expansion**: The existing feature for expanding technical abbreviations (to be merged)
- **Synonym_Mapping**: The existing feature for mapping synonymous terms (merge target)
- **Intelligent_Cleaning**: The existing feature containing 4 sub-features (to be split)
- **Configuration_Migration**: The process of preserving existing configuration data during restructuring
- **Text_Cleaning**: Noise filtering, metadata processing, and separator unification
- **Normalization_Mapping**: Character-level text replacements
- **Feature_Extraction**: Processing separators, parameter decomposition, smart splitting, and unit removal
- **Feature_Quality**: Quality scoring and whitelist management

## Requirements

### Requirement 1: Workflow-Based Menu Organization

**User Story:** As a system administrator, I want the configuration menu organized by workflow stages, so that I can easily find configurations relevant to each processing phase.

#### Acceptance Criteria

1. THE ConfigManagementView SHALL display menu items grouped into 5 workflow stages: Pre-entry Configuration, Data Import Stage, Preprocessing Configuration, Matching Configuration, and Global Configuration
2. WHEN a user views the menu THEN THE ConfigManagementView SHALL display stage names with appropriate icons (📝, 📥, 🔍, 🎯, ⚙️)
3. WHEN a user navigates through stages THEN THE ConfigManagementView SHALL maintain the logical order: Pre-entry → Import → Preprocessing → Matching → Global
4. THE ConfigManagementView SHALL display all menu items within their corresponding workflow stage

### Requirement 2: Hierarchical Sub-Menu Support

**User Story:** As a system administrator, I want to see sub-menus under complex configuration sections, so that I can navigate through related configurations more easily.

#### Acceptance Criteria

1. THE ConfigManagementView SHALL support 2-level menu hierarchy (parent menu items and sub-menu items)
2. WHEN a user clicks a parent menu item with sub-items THEN THE ConfigManagementView SHALL expand to show all sub-menu items
3. WHEN a user clicks a parent menu item without sub-items THEN THE ConfigManagementView SHALL navigate directly to that configuration page
4. THE ConfigManagementView SHALL display the Preprocessing Configuration stage with 4 sub-sections: Text Cleaning, Normalization Mapping, Feature Extraction, and Feature Quality
5. THE ConfigManagementView SHALL display the Text Cleaning sub-section with 3 configuration pages: Noise Filtering, Metadata Processing, and Separator Unification
6. THE ConfigManagementView SHALL display the Feature Extraction sub-section with 4 configuration pages: Separator Processing, Complex Parameter Decomposition, Smart Splitting, and Unit Removal
7. THE ConfigManagementView SHALL display the Feature Quality sub-section with 2 configuration pages: Quality Scoring and Whitelist

### Requirement 3: Merge Duplicate Features

**User Story:** As a system administrator, I want technical term expansion and synonym mapping merged into a single interface, so that I don't have to manage word-level replacements in two separate places.

#### Acceptance Criteria

1. THE ConfigManagementView SHALL display a single "Synonym Mapping" menu item under Matching Configuration stage
2. WHEN a user opens Synonym Mapping THEN THE System SHALL display both synonym mappings and technical term expansions in a unified interface
3. WHEN a user adds a mapping THEN THE System SHALL allow specifying whether it is a synonym or technical term expansion
4. THE System SHALL preserve all existing technical term expansion data during the merge
5. THE System SHALL preserve all existing synonym mapping data during the merge

### Requirement 4: Split Intelligent Cleaning Feature

**User Story:** As a system administrator, I want the intelligent cleaning feature split into logical sub-sections, so that I can configure each preprocessing step independently.

#### Acceptance Criteria

1. THE ConfigManagementView SHALL NOT display a single "Intelligent Cleaning" menu item
2. THE ConfigManagementView SHALL display separate menu items for Text Cleaning, Normalization Mapping, Feature Extraction, and Feature Quality under Preprocessing Configuration
3. WHEN a user opens Text Cleaning THEN THE System SHALL display configurations for noise filtering, metadata processing, and separator unification
4. WHEN a user opens Normalization Mapping THEN THE System SHALL display character-level replacement configurations
5. WHEN a user opens Feature Extraction THEN THE System SHALL display configurations for separator processing, parameter decomposition, smart splitting, and unit removal
6. WHEN a user opens Feature Quality THEN THE System SHALL display configurations for quality scoring and whitelist management
7. THE System SHALL preserve all existing intelligent cleaning configuration data during the split

### Requirement 5: Configuration Data Migration

**User Story:** As a system administrator, I want all existing configurations preserved during the menu restructuring, so that I don't lose any configuration data.

#### Acceptance Criteria

1. WHEN the restructured menu is deployed THEN THE System SHALL preserve all existing configuration data in the database
2. WHEN technical term expansion is merged with synonym mapping THEN THE System SHALL maintain backward compatibility with existing API endpoints
3. WHEN intelligent cleaning is split THEN THE System SHALL map existing configuration data to the appropriate new sub-sections
4. THE System SHALL NOT require manual re-entry of any existing configuration data
5. WHEN a user accesses any configuration page THEN THE System SHALL display all previously saved configuration values

### Requirement 6: Preserve All Existing Functionality

**User Story:** As a system administrator, I want all existing configuration features to work exactly as before, so that the restructuring doesn't break any functionality.

#### Acceptance Criteria

1. THE System SHALL maintain all existing configuration save operations
2. THE System SHALL maintain all existing configuration load operations
3. THE System SHALL maintain all existing configuration validation rules
4. WHEN a user saves a configuration THEN THE System SHALL apply it to the device matching process exactly as before
5. THE System SHALL maintain all existing API endpoints for configuration management
6. THE TextPreprocessor SHALL continue to execute preprocessing steps in the same order
7. THE MatchEngine SHALL continue to apply matching configurations in the same way

### Requirement 7: Menu Navigation and State Management

**User Story:** As a system administrator, I want the menu to remember my current location and expand/collapse state, so that I can navigate efficiently.

#### Acceptance Criteria

1. WHEN a user selects a menu item THEN THE ConfigManagementView SHALL highlight the active menu item
2. WHEN a user expands a sub-menu THEN THE ConfigManagementView SHALL maintain the expanded state until the user collapses it
3. WHEN a user navigates to a sub-menu item THEN THE ConfigManagementView SHALL automatically expand the parent menu
4. WHEN a user refreshes the page THEN THE ConfigManagementView SHALL restore the previously selected menu item
5. THE ConfigManagementView SHALL display visual indicators for expanded/collapsed sub-menus

### Requirement 8: Pre-Entry Configuration Stage

**User Story:** As a system administrator, I want to configure settings that apply before device information is entered, so that I can set up the system properly.

#### Acceptance Criteria

1. THE ConfigManagementView SHALL display a "Pre-entry Configuration" stage with 3 menu items: Brand Keywords, Device Parameters, and Feature Weights
2. WHEN a user opens Brand Keywords THEN THE System SHALL display the brand keyword configuration interface
3. WHEN a user opens Device Parameters THEN THE System SHALL display the device parameter configuration interface
4. WHEN a user opens Feature Weights THEN THE System SHALL display the feature weight configuration interface

### Requirement 9: Data Import Stage

**User Story:** As a system administrator, I want to configure how device rows are recognized during data import, so that the system correctly identifies device information.

#### Acceptance Criteria

1. THE ConfigManagementView SHALL display a "Data Import Stage" with 1 menu item: Device Row Recognition
2. WHEN a user opens Device Row Recognition THEN THE System SHALL display the device row recognition configuration interface

### Requirement 10: Matching Configuration Stage

**User Story:** As a system administrator, I want to configure matching behavior, so that the system matches devices according to my requirements.

#### Acceptance Criteria

1. THE ConfigManagementView SHALL display a "Matching Configuration" stage with 3 menu items: Synonym Mapping, Device Type Keywords, and Match Threshold
2. WHEN a user opens Synonym Mapping THEN THE System SHALL display the unified synonym and technical term mapping interface
3. WHEN a user opens Device Type Keywords THEN THE System SHALL display the device type keyword configuration interface
4. WHEN a user opens Match Threshold THEN THE System SHALL display the match threshold configuration interface

### Requirement 11: Global Configuration Stage

**User Story:** As a system administrator, I want to configure system-wide settings, so that I can control global behavior.

#### Acceptance Criteria

1. THE ConfigManagementView SHALL display a "Global Configuration" stage with 1 menu item: Global Settings
2. WHEN a user opens Global Settings THEN THE System SHALL display the global configuration interface
