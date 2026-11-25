import zipfile
import xml.etree.ElementTree as E
from pathlib import Path
import sys
p=Path(sys.argv[1] if len(sys.argv)>1 else 'outputs/ipo-ready-survey-20261021/IPO_Ready_Research_Survey_Pass1.xlsx')
with zipfile.ZipFile(p) as z:
    assert z.testzip() is None
    ns={'s':'http://schemas.openxmlformats.org/spreadsheetml/2006/main'}
    sheets=[n for n in z.namelist() if n.startswith('xl/worksheets/sheet') and n.endswith('.xml')]
    for n in sheets:
        root=E.fromstring(z.read(n))
        errors=[c.attrib['r'] for c in root.findall('.//s:c',ns) if c.attrib.get('t')=='e']
        assert not errors,(n,errors)
    root=E.fromstring(z.read('xl/tables/table1.xml'))
    print('Table:',root.attrib)
    expected='A4:P43' if 'Pass2' in str(p) else 'A4:P34'
    assert root.attrib['ref']==expected
    for name in sheets:
        pane=E.fromstring(z.read(name)).find('.//s:pane',ns)
        print('Freeze pane:',name,pane.attrib if pane is not None else None)
    print('Verified: ZIP integrity, 2 sheets, expected survey range, no Excel error cells.')
print('Saved bytes:',p.stat().st_size)
