"""Create a small course-facing notebook and execute its code cells for verification."""
from pathlib import Path
import json
ROOT=Path(__file__).resolve().parents[1]
cells=[]
def md(s):cells.append({'cell_type':'markdown','metadata':{},'source':s.splitlines(True)})
def code(s):cells.append({'cell_type':'code','metadata':{},'execution_count':None,'outputs':[],'source':s.splitlines(True)})
md('# IPO-Ready: Python financial analytics baseline\n\nRetrospective Aether RHP pilot. Curated transcription, not automatic extraction. Monetary inputs are INR million; EPS is INR/share. Run from the project root or notebooks folder. No model or investment recommendation.\n')
code("from pathlib import Path\nimport json\nimport pandas as pd\nroot = Path.cwd() if (Path.cwd() / 'research').exists() else Path.cwd().parent\npilot = json.loads((root / 'research/aether_reconciliation/pilot_data.json').read_text())\nperiods = ['9M Dec-2021', '9M Dec-2020', 'FY21', 'FY20', 'FY19']\nrows = []\nfor row in pilot['raw']:\n    for i, period in enumerate(periods):\n        rows.append({'metric': row[0], 'period': period, 'value': row[i+1], 'unit': row[6], 'pdf_page': row[7], 'basis': row[9]})\nfacts = pd.DataFrame(rows)\nassert len(facts) == 110\nfacts.head()\n")
md('## Prepare comparable annual observations\n\nKeep interim periods separate. Revenue and cash figures below are converted from million to crore by dividing by ten. EPS must not receive that conversion.\n')
code("annual = facts[facts.period.isin(['FY19', 'FY20', 'FY21'])].pivot(index='period', columns='metric', values='value').reindex(['FY19','FY20','FY21'])\nprofile = pd.DataFrame(index=annual.index)\nprofile['Revenue (INR crore)'] = annual['Revenue from operations'] / 10\nprofile['PAT (INR crore)'] = annual['Profit after tax'] / 10\nprofile['CFO (INR crore)'] = annual['Net cash from operating activities'] / 10\nprofile['EBITDA margin'] = annual['EBITDA excluding other income'] / annual['Revenue from operations']\nprofile['CFO/PAT'] = annual['Net cash from operating activities'] / annual['Profit after tax']\nprofile['Borrowings/equity'] = annual['Debt as disclosed'] / annual['Total equity']\nprofile\n")
md('## Growth and reconciliation\n\nUse two elapsed years from FY19 to FY21. These internal checks do not establish financial health or validate transcription against the original PDF.\n')
code("revenue_cagr = (annual.loc['FY21','Revenue from operations'] / annual.loc['FY19','Revenue from operations']) ** (1/2) - 1\nresidual = annual['Revenue from operations'] + annual['Other income'] - annual['Total income']\nassert residual.abs().max() <= 0.02\nassert abs(profile.loc['FY21', 'CFO/PAT'] - 231.96/711.19) < 1e-12\nprint(f'Revenue CAGR FY19-FY21: {revenue_cagr:.2%}')\nprint(profile.round(3).to_string())\noutput = root / 'outputs/poc'\noutput.mkdir(parents=True, exist_ok=True)\nprofile.to_csv(output / 'aether_annual_profile.csv')\n")
md('## Interpretation and unresolved issues\n\nRevenue and PAT growth should be considered alongside cash conversion. CFO/PAT is descriptive, not a distress probability. The pilot retains conflicting repeated Dec-2020 asset values and unresolved valuation inputs. Source: '+ 'https://www.sebi.gov.in/sebi_data/attachdocs/may-2022/1652869529567.pdf' +' (physical pp.64-67, 302-303).\n\nThe web demo adds evidence drill-down and an executed deterministic workflow trace. Model-selected actions and automatic extraction are future milestones.\n')
out=ROOT/'notebooks/01_financial_analysis.ipynb';out.parent.mkdir(exist_ok=True)
out.write_text(json.dumps({'cells':cells,'metadata':{'kernelspec':{'display_name':'Python 3','language':'python','name':'python3'},'language_info':{'name':'python','version':'3.11'}},'nbformat':4,'nbformat_minor':5},indent=2),encoding='utf8')
scope={}
for cell in cells:
    if cell['cell_type']=='code':exec(''.join(cell['source']),scope)
print('Notebook code cells executed successfully; saved notebook remains clean for classroom use.')
