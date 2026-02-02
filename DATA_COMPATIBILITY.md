# Data Compatibility & Architecture

## How Data Flows Through The System

### 1. Original Scraping (Creates Old Format Dumps)

When you run the scraper in **Company Mode** or **Financial Mode**, it creates dump files with this structure:

```json
{
  "company_name": "Example Corp",
  "mode": "COMPANY",
  "signals": [
    {
      "id": "sig_1",
      "source_type": "news",
      "extracted_text": "...",
      "metadata": {...}
    }
  ],
  "financial_data": {...},
  "timestamp": "2026-01-30T15:17:21"
}
```

**File naming:** `company_20260130_151721.json`

This is the **OLD/ORIGINAL format** - just raw scraped data.

### 2. Hypothesis Analysis (Creates New Format Results)

When you run hypothesis analysis, it:

- ✅ **Reads** old dump files (original format)
- ✅ **Processes** the raw signals with AI
- ✅ **Generates** new analysis structure
- ✅ **Does NOT modify** the original dump files

The analysis output has this **NEW format**:

```json
{
  "company_name": "Example Corp",
  "analysis_timestamp": "2026-02-02T10:30:00",
  "risk_summary": {
    "overall_risk": "high",
    "confidence": "high",
    "summary": "...",
    "recommendation": "..."
  },
  "primary_signals": [
    {
      "id": "ps_1",
      "title": "OPERATIONAL DEGRADATION",
      "description": "...",
      "supporting_signal_ids": ["ss_1", "ss_2"]
    }
  ],
  "supporting_signals": [
    {
      "id": "ss_1",
      "title": "Scale Decay & Branch Closures",
      "evidence": "..."
    }
  ]
}
```

## Backward Compatibility Strategy

### ✅ Old Dumps Are Preserved

- Original scraping dumps remain unchanged
- They can still be loaded and viewed normally
- The DumpBrowser component displays them correctly
- They serve as the source data for hypothesis analysis

### ✅ New Analysis Results Are Separate

- Hypothesis analysis generates new output
- Can be saved as separate files (e.g., `hypothesis_analysis_company.json`)
- Frontend components know which format they're displaying

### ✅ Components Handle Both Formats

#### DumpBrowser Component

- Displays OLD format (raw scraping results)
- Shows signals list as before
- No changes needed

#### HypothesisViewer Component

- Always displays NEW format (analysis results)
- Calls API to generate fresh analysis
- Works with any old dump as input

## Component Architecture

```
┌─────────────────────────────────────────────────────────┐
│                    Main Scraper Page                     │
│              (Company/Financial Mode)                    │
└────────────────────┬────────────────────────────────────┘
                     │
                     ▼
              ┌─────────────┐
              │  OLD DUMPS  │  ← Original format
              │  Raw Data   │     (signals, financial_data)
              └──────┬──────┘
                     │
        ┌────────────┼────────────┐
        │                         │
        ▼                         ▼
┌──────────────┐        ┌─────────────────┐
│ DumpBrowser  │        │ Hypothesis API  │
│  Component   │        │    Analysis     │
│              │        └────────┬────────┘
│ Displays:    │                 │
│ - Raw signals│                 ▼
│ - Metadata   │         ┌──────────────┐
│ - Stats      │         │ NEW ANALYSIS │ ← New format
└──────────────┘         │   Results    │   (primary/supporting)
                         └──────┬───────┘
                                │
                                ▼
                       ┌────────────────┐
                       │ HypothesisViewer│
                       │   Component     │
                       │                 │
                       │ Displays:       │
                       │ - Primary       │
                       │ - Supporting    │
                       │ - Evidence      │
                       └─────────────────┘
```

## Usage Workflow

### For Users With Old Dumps:

1. **Old dumps work perfectly** - they're used as input
2. Go to `/hypothesis` page
3. Enter company name
4. System finds old dumps automatically
5. Generates new analysis on the fly
6. Displays results in new format

### For New Users:

1. First scrape company data (creates old format dump)
2. Then run hypothesis analysis (generates new format)
3. Both formats coexist peacefully

## File Structure

```
backend-py/dumps/
├── company_20260130_151721.json          ← OLD format (raw data)
├── company_20260130_094744.json          ← OLD format (raw data)
├── hypothesis_analysis_example.json      ← NEW format (if saved)
└── README.md
```

## Key Points

✅ **No Breaking Changes**

- Old dumps still work perfectly
- Can be viewed in DumpBrowser
- Serve as source for analysis

✅ **Separate Concerns**

- Scraping → Creates raw data (old format)
- Analysis → Processes data (new format)
- Components → Know what to display

✅ **Future Proof**

- New features don't affect old data
- Analysis can be re-run anytime
- Multiple analyses from same dump

## FAQ

**Q: Do I need to re-scrape old data?**
A: No! Old dumps work perfectly as input for hypothesis analysis.

**Q: Will my old dumps be modified?**
A: No, they remain unchanged. Analysis creates new output.

**Q: Can I still view old dumps?**
A: Yes, DumpBrowser component displays them normally.

**Q: What if I want to save analysis results?**
A: The test script saves them as separate files. You can add this to the UI too.

**Q: Can I run analysis multiple times?**
A: Yes! Each analysis is independent and doesn't modify source data.
