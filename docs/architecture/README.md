# IPO-Ready target fintech product architecture

Revision 2, 29 October 2026. This replaces the earlier prototype-anchored framing with a target product architecture for company discovery, comparison, evaluation, shortlisting and monitoring.

Start with `IPO_Ready_Architecture_Design.pdf`: seven views, an A2 vector overview and six A3 supporting pages. `IPO_Ready_Editable_Diagrams.drawio` contains the editable pages for diagrams.net. Each view is also an SVG.

`IPO_Ready_Design_Framework.md` covers product domains, intelligence/ranking models, data roles, runtime contracts, coherent publication, model evaluation and growth. Mermaid alternatives and an Eraser AI brief are included.

To rebuild: `python tools/build_product_architecture.py .` from this directory. Requires Python/ReportLab. DejaVu Sans is used when available at the paths in `tools/product_diagram_engine.py`; PDF otherwise falls back to Helvetica.

Repository/attachments provide context, not architectural constraints. Data access is assumed adequate for this proposal. All components, technology choices and models shown are proposed; no production deployment or validated investment model is claimed.
