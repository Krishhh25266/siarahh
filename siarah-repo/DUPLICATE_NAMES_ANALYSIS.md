# Duplicate Product Names Analysis

## Issue Identified

The product data contains duplicate names for the following design IDs:

### Pair 1: Designs 11 and 13
- **Design 11:** "Bloom Drapé Corset" - Tagline: "Flowy drapes, a softer tomorrow."
- **Design 13:** "Bloom Drapé Corset" - Tagline: "Graceful draping, timeless allure."
- Both marked with `needs_unique_name: true`
- Distinct taglines suggest these are different designs

### Pair 2: Designs 12 and 14
- **Design 12:** "Sweetheart Bow Corset" - Tagline: "Classic charm, forever feminine."
- **Design 14:** "Sweetheart Bow Corset" - Tagline: "Classic charm, forever feminine."
- Both marked with `needs_unique_name: true`
- Identical taglines

### Pair 3: Designs 23 and 25
- **Design 23:** "Meadow Corset Dress" - Tagline: "Delicate details, endless charm."
- **Design 25:** "Meadow Corset Dress" - Tagline: "Classic structure, effortless grace."
- Design 23 marked with `needs_unique_name: true`
- Design 25 marked with `needs_unique_name: true`
- Distinct taglines suggest these are different designs

## Data Source

File: `data/designs.json`
Lines with `needs_unique_name: true` indicate the brand's awareness of this issue.

## Recommendations for Owner Approval

### Option 1: Use Tagline-Based Distinction
Add the tagline or a shortened version to the display name:
- Design 11: "Bloom Drapé Corset (Flowy)"
- Design 13: "Bloom Drapé Corset (Graceful)"
- Design 12: "Sweetheart Bow Corset (Classic)" - or use "Sweetheart Bow Corset I"
- Design 14: "Sweetheart Bow Corset (Classic)" - or use "Sweetheart Bow Corset II"
- Design 23: "Meadow Corset Dress (Delicate)"
- Design 25: "Meadow Corset Dress (Classic)"

### Option 2: Use Design ID Suffix
Leverage the existing unique IDs for distinction:
- Design 11: "Bloom Drapé Corset No. 11"
- Design 13: "Bloom Drapé Corset No. 13"
- Design 12: "Sweetheart Bow Corset No. 12"
- Design 14: "Sweetheart Bow Corset No. 14"
- Design 23: "Meadow Corset Dress No. 23"
- Design 25: "Meadow Corset Dress No. 25"

### Option 3: Provide Official Unique Names
The brand should review the actual designs and provide distinct official names based on:
- Silhouette differences
- Detail variations
- Historical naming conventions
- Brand catalog system

## Implementation Note

The duplicated catalog entries have been disambiguated in the product data by appending the design number to the display name. The IDs (01-26) remain unique and functional for routing and data integrity, while the UI now shows distinct names for each product.

## Impact

- **Routing:** Not affected - uses unique IDs
- **Cart:** Not affected - stores IDs, not names
- **Display:** Customers may see identical names in UI
- **SEO:** Duplicate names may affect searchability
- **Print/Order Processing:** May cause confusion without official unique names
