# V2 review repairs for Polymatech and IGX

24 November 2026 · V2-02. [Archived reproduction](../../../archive/v1-handoff-20261124/docs/starter-kit/REVIEW.md)

## Polymatech

The retained WWIPL consolidated P&L dated 31 March 2025 has distinct rows for profit before the associate share, associate profit, final consolidated PAT and the amount attributable to owners. In physical HTML table index 2 the zero-based source row positions used by the parser are 15–18. Reported basic and diluted EPS are in rows 30–31. The later owner-attribution row is part of comprehensive income. The provider capture dated 23 November 2026 also carries the ₹36 indicative quote and 398,438,875 shares. [Financial capture](../../../data/captures/wwipl/20261123T164433Z/polymatech-financial.html) · [Overview capture](../../../data/captures/wwipl/20261123T164433Z/polymatech-overview.html) · [Capture hashes](../../../data/captures/wwipl/20261123T164433Z/manifest.json) · [Provider financial statements](https://wwipl.com/unlisted-shares/polymatech-electronics-share-price/financial)

| Observation | Reported | Normalized |
| --- | ---: | ---: |
| PAT before associate | ₹37,501.16 lakh | ₹375.0116 crore |
| Associate contribution | ₹57.48 lakh | ₹0.5748 crore |
| Final consolidated PAT | ₹37,558.64 lakh | ₹375.5864 crore |
| Attributable to owners | ₹36,136.63 lakh | ₹361.3663 crore |
| Basic and diluted EPS | ₹9.07 each | ₹9.07 each |

The reviewed subtotal plus the associate contribution equals final PAT. The parser requires a final row label and preserves conflicts when competing final lines disagree on the same table and scope. The Group Pharmaceuticals conflict still reproduces. Dividing ₹36 by ₹9.07 gives **3.9691×**. Using total PAT per ending share produces **3.8190×** after division with full precision. The proxy differs in earnings scope and share denominator. Annual basic EPS is the default where sourced, and a separately named proxy field supports controlled comparison with the legacy calculation. The default 3.82× and 3.90× boundaries exclude Polymatech, while 15× and the explicit 3.82× proxy boundary include it under the same other screen conditions.

## IGX

The restated issuer balance sheet covers FY2024–FY2026. The inventory turnover note says the measure is inapplicable to the business. Use the issuer current asset and liability totals and assume nil inventory only within the supported balance-sheet years. FY2026 uses ₹445.937 crore and ₹294.599 crore, giving **1.5137×**. That assumption is distinct from an explicit reported zero. FY2022 remains unavailable from this evidence. The dashboard drawer links both assets and liabilities to physical page 5 and the inventory note to page 54. [Restated balance sheet, p. 5](https://testwebcms.igxindia.com/files/financials-5bCIC136dXcpEa1daoEb.pdf#page=5) · [Inventory note, p. 54](https://testwebcms.igxindia.com/files/financials-5bCIC136dXcpEa1daoEb.pdf#page=54)

The same filing reports FY2026 basic EPS of ₹5.68 and diluted EPS of ₹5.66. The indicative ₹488 price produces **85.9155×** using basic EPS. The source date and its trust scope travel with the ratio. Retaining the earlier provider proxy as a separate record makes differences easy to trace. [Restated P&L, p. 6](https://testwebcms.igxindia.com/files/financials-5bCIC136dXcpEa1daoEb.pdf#page=6)

The draft prospectus reports FY2026, FY2025 and FY2024 traded gas volume of 76.79, 60.02 and 40.84 million MMBtu, with transaction fees net of revenue reversals of ₹575.72, ₹450.05 and ₹306.50 million. The matched FY2026 observations give **27.9407%** traded-volume growth and **₹7.4973 per MMBtu**. These are exchange activity measures with a defined venue and periods. [Draft prospectus, 14 July 2026, p. 30](https://testwebcms.igxindia.com/files/drhp-6w0Qkr9JEHUyvsQQbc1.pdf#page=30) · [Retained issuer file and digest](../../../data/captures/issuer/20261123T163845Z/manifest.json)
