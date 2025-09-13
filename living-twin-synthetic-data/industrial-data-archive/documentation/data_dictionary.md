# Industrial Companies Dataset - Data Dictionary

## Overview

This document provides comprehensive field definitions and data specifications for the Industrial Companies Dataset. The dataset contains 500 synthetic company records with 24 primary fields covering business, financial, and operational characteristics.

## Core Data Structure

### Company Identification
| Field | Type | Description | Example |
|-------|------|-------------|---------|
| `id` | String | Unique company identifier | `"asian_industrial_042"` |
| `name` | String | Company legal name | `"Advanced Manufacturing Technologies Corp."` |
| `source` | String | Data generation source | `"Asian Industrial Database"` |
| `scraped_date` | ISO Date | Dataset generation timestamp | `"2025-09-13T22:22:28.628398"` |

### Industry Classification
| Field | Type | Description | Values/Range |
|-------|------|-------------|--------------|
| `industry` | String | Specific industry vertical | See [Industry Categories](#industry-categories) |
| `sector` | String | Major economic sector | `Manufacturing`, `Energy`, `Infrastructure`, `Technology` |
| `subsector` | String | Detailed industry subsector | `Vehicle Assembly`, `Solar Power`, `Network Infrastructure`, etc. |

### Geographic Information
| Field | Type | Description | Format |
|-------|------|-------------|---------|
| `headquarters` | String | Primary business location | `"City, Country"` format |
| `country` | String | Headquarters country | ISO country names |
| `region` | String | Major geographic region | See [Regional Categories](#regional-categories) |
| `locations` | Array[String] | Global operational locations | Array of `"City, Country"` strings |

### Financial Metrics
| Field | Type | Description | Range/Format |
|-------|------|-------------|--------------|
| `revenue` | String | Annual revenue (formatted) | `"$X.XB"` format |
| `revenue_numeric` | Float | Annual revenue in billions USD | 0.1 - 500.0 |
| `market_cap` | String | Market capitalization | `"$X.XB"` format |
| `employees` | Integer | Total employee count | 100 - 1,500,000 |

### Operational Details
| Field | Type | Description | Content |
|-------|------|-------------|---------|
| `founded` | Integer | Company founding year | 1890 - 2020 |
| `ceo` | String | Chief Executive Officer name | Culturally appropriate names |
| `website` | String | Company website URL | Generated based on company name |
| `description` | String | Business description | Industry-appropriate description |

### Business Portfolio
| Field | Type | Description | Content |
|-------|------|-------------|---------|
| `products` | Array[String] | Product offerings | 3-6 industry-specific products |
| `services` | Array[String] | Service offerings | 2-5 professional services |
| `subsidiaries` | Array[String] | Subsidiary companies | 0-5 related business entities |

### Stock Market Information
| Field | Type | Description | Format |
|-------|------|-------------|---------|
| `stock_exchange` | String | Primary stock exchange | Exchange names by country |
| `ticker` | String | Stock ticker symbol | 2-4 character codes with country suffix |

### Quality & Compliance
| Field | Type | Description | Content |
|-------|------|-------------|---------|
| `certifications` | Array[String] | Industry certifications | 3-7 relevant standards/certifications |

### Innovation & Performance Metrics
| Field | Type | Description | Range |
|-------|------|-------------|-------|
| `sustainability_score` | Float | ESG/sustainability rating | 0.0 - 1.0 |
| `innovation_index` | Float | Innovation capability score | 0.0 - 1.0 |
| `digital_maturity` | Float | Digital transformation score | 0.0 - 1.0 |

## Detailed Field Specifications

### Industry Categories

#### Manufacturing Sector
- **Automotive**: Vehicle assembly, auto parts, electric vehicles, autonomous systems
- **Aerospace & Defense**: Commercial aircraft, military aircraft, space systems, defense equipment
- **Machinery**: Industrial machinery, construction equipment, agricultural equipment, mining equipment
- **Electronics**: Consumer electronics, industrial electronics, telecommunications equipment, test equipment
- **Chemicals**: Basic chemicals, specialty chemicals, petrochemicals, agricultural chemicals
- **Pharmaceuticals**: Prescription drugs, generic drugs, biotechnology, medical devices
- **Food & Beverage**: Food processing, beverage manufacturing, packaging, food safety
- **Textiles**: Apparel manufacturing, technical textiles, home textiles, industrial fabrics
- **Metals**: Steel production, aluminum, copper, precious metals
- **Plastics**: Polymer production, plastic components, packaging materials, composite materials

#### Energy Sector
- **Oil & Gas**: Upstream operations, refining, petrochemicals, distribution
- **Renewable Energy**: Solar power, wind power, hydroelectric, geothermal
- **Utilities**: Electric power, natural gas distribution, water treatment, waste management
- **Mining**: Coal mining, metal mining, industrial minerals, rare earth elements
- **Nuclear**: Nuclear power generation, nuclear technology, nuclear services, waste management

#### Infrastructure Sector
- **Construction**: Commercial construction, infrastructure projects, residential construction, industrial construction
- **Transportation**: Railway systems, aviation infrastructure, maritime infrastructure, urban transport
- **Logistics**: Supply chain management, warehousing, distribution, third-party logistics
- **Telecommunications**: Network infrastructure, wireless technology, fiber optics, 5G technology
- **Real Estate**: Industrial real estate, commercial development, infrastructure investment, property management

#### Technology Sector
- **Semiconductors**: Chip manufacturing, semiconductor equipment, electronic components, memory devices
- **Software**: Enterprise software, industrial software, ERP systems, manufacturing execution
- **Hardware**: Computer hardware, server systems, industrial computers, embedded systems
- **AI/ML**: Artificial intelligence, machine learning platforms, computer vision, robotics AI
- **IoT**: Industrial IoT, smart sensors, connected devices, edge computing
- **Robotics**: Industrial robots, service robots, automation systems, robotic components

### Regional Categories

| Region | Countries Included |
|--------|-------------------|
| **North America** | United States, Canada, Mexico |
| **Europe** | Germany, UK, France, Italy, Spain, Netherlands, Switzerland, Sweden, Norway, Denmark, Austria, Belgium, Poland |
| **Asia Pacific** | China, Japan, South Korea, India, Singapore, Taiwan, Australia, Thailand, Malaysia, Indonesia, Philippines, Vietnam |
| **Latin America** | Brazil, Argentina, Chile, Colombia, Peru, Venezuela, Ecuador |
| **Middle East & Africa** | Saudi Arabia, UAE, Qatar, South Africa, Egypt, Nigeria, Turkey, Israel, Morocco |

### Stock Exchange Mapping

| Country/Region | Primary Exchange | Ticker Format |
|----------------|------------------|---------------|
| United States | NYSE/NASDAQ | `ABCD` |
| Germany | Frankfurt Stock Exchange | `ABCD.DE` |
| United Kingdom | London Stock Exchange | `ABCD.L` |
| France | Euronext Paris | `ABCD.PA` |
| Japan | Tokyo Stock Exchange | `ABCD.T` |
| China | Shanghai/Shenzhen | `ABCD.SS/.SZ` |
| South Korea | Korea Exchange | `ABCD.KS` |
| India | BSE/NSE | `ABCD.NS/.BO` |

### Certification Standards by Industry

#### Manufacturing Standards
- **ISO 9001:2015**: Quality management systems
- **ISO 14001:2015**: Environmental management systems
- **ISO 45001:2018**: Occupational health and safety
- **IATF 16949**: Automotive quality management
- **AS9100**: Aerospace quality management
- **IPC Standards**: Electronics manufacturing standards

#### Industry-Specific Certifications
- **Pharmaceuticals**: FDA Approved, GMP Certified, ISO 13485, EMA Certified
- **Oil & Gas**: API Standards, ISO 29001, NORSOK Standards
- **Food & Beverage**: HACCP, FDA Food Safety, USDA Organic
- **Electronics**: UL Listed, CE Marking, FCC Approved, RoHS Compliant

## Data Quality Specifications

### Value Ranges and Constraints

#### Financial Metrics
- **Revenue Range**: $0.1B - $500B (realistic Fortune 500 scale)
- **Employee Range**: 100 - 1,500,000 (enterprise scale)
- **Market Cap Range**: Calculated as 1.5x - 4.0x revenue
- **Revenue-per-Employee**: Industry-specific ratios (200K - 800K USD)

#### Performance Scores
- **All Scores**: 0.0 - 1.0 (normalized scale)
- **Distribution**: Random with industry bias adjustments
- **Sustainability**: Higher scores for renewable energy companies
- **Innovation**: Higher scores for technology companies
- **Digital Maturity**: Higher scores for software/tech companies

#### Geographic Distribution
- **Regional Balance**: Asia Pacific (30%), North America (25%), Europe (25%)
- **Country Coverage**: 58 countries represented
- **Business Hub Concentration**: Major companies in economic centers

### Data Validation Rules

#### Consistency Rules
1. **Revenue-Employee Correlation**: Revenue per employee within industry norms
2. **Geographic Alignment**: Headquarters country matches region assignment
3. **Industry Alignment**: Products/services match industry classification
4. **Certification Relevance**: All certifications appropriate for industry/geography

#### Completeness Requirements
1. **Mandatory Fields**: All 24 fields must be populated
2. **Array Minimums**: Products (2+), Services (2+), Certifications (3+)
3. **Valid Formats**: Dates in ISO format, revenues in consistent format
4. **No Null Values**: All critical business metrics must have valid values

## Usage Guidelines

### Field Selection for Analysis
- **Financial Analysis**: Use `revenue_numeric`, `employees`, `market_cap`
- **Geographic Analysis**: Use `region`, `country`, `locations`
- **Industry Analysis**: Use `sector`, `industry`, `subsector`
- **Innovation Studies**: Use `innovation_index`, `digital_maturity`, `sustainability_score`

### Data Interpretation Notes
- **Revenue Figures**: All in USD billions for consistency
- **Employee Counts**: Total global workforce including subsidiaries
- **Scores**: Relative rankings within dataset, not absolute benchmarks
- **Geographic Data**: Headquarters location, not necessarily largest operation

### Common Use Cases
1. **Market Segmentation**: Group by `sector`, `region`, `revenue_numeric`
2. **Competitive Analysis**: Sort by `revenue_numeric` within `industry`
3. **Innovation Studies**: Analyze `innovation_index` patterns by `sector`
4. **Global Operations**: Study `locations` patterns by company size

---

This data dictionary provides the foundation for understanding and effectively utilizing the Industrial Companies Dataset for AI training and business analysis applications.