# Sample Datasets

Ready-to-upload sample financial data files for testing the platform.

## Files

| File | Company | Periods | Format |
|------|---------|---------|--------|
| `apple_financials_2023.csv` | Apple Inc. | 2021, 2022, 2023 | Multi-period CSV |
| `tesla_financials_2023.csv` | Tesla Inc. | 2021, 2022, 2023 | Multi-period CSV |

## How to Use

1. Go to **Companies** → Add "Apple Inc." (ticker: AAPL, sector: Technology)
2. Go to **Upload Statement**
3. Select the company
4. Set Period = `2023-FY`, Period Type = `annual`
5. Upload `apple_financials_2023.csv`
6. The system auto-detects all 3 years and imports them

Then head to **AI Insights** to generate a full analysis!

## Custom Data Format

Your CSV should look like this:
```
Metric,Value
Revenue,394328000000
Net Income,99803000000
Total Assets,352755000000
...
```

Or multi-period:
```
Metric,2021,2022,2023
Revenue,365817000000,394328000000,383285000000
...
```
