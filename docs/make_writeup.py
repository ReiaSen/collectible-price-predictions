import json
from reportlab.lib.pagesizes import A4
from reportlab.lib.units import mm
from reportlab.lib import colors
from reportlab.lib.styles import ParagraphStyle
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, Image

M = json.load(open("results/metrics.json")); mo = M["models"]
body = ParagraphStyle("b", fontName="Helvetica", fontSize=8.6, leading=11, spaceAfter=3)
h = ParagraphStyle("h", fontName="Helvetica-Bold", fontSize=10.5, leading=13, spaceBefore=5, spaceAfter=2, textColor=colors.HexColor("#1a365d"))
title = ParagraphStyle("t", fontName="Helvetica-Bold", fontSize=14.5, leading=17, spaceAfter=2)
sub = ParagraphStyle("s", fontName="Helvetica", fontSize=8.8, leading=11, textColor=colors.HexColor("#4a5568"))
bul = ParagraphStyle("bl", parent=body, leftIndent=10, bulletIndent=2, spaceAfter=1.5)
note = ParagraphStyle("n", parent=body, backColor=colors.HexColor("#fffaf0"), borderColor=colors.HexColor("#dd6b20"), borderWidth=0.7, borderPadding=4, spaceBefore=3, spaceAfter=6)
doc = SimpleDocTemplate("Team30_Problem50_Writeup.pdf", pagesize=A4, leftMargin=16*mm, rightMargin=16*mm, topMargin=13*mm, bottomMargin=12*mm,
                        title="Collectible Merchandise Price Prediction", author="Reia S, Ritesh Babu Reddy")
v = lambda n, k: mo[n]["valid"][k]
S = [Paragraph("Collectible Merchandise Price Prediction: A Machine Learning Case Study", title),
     Paragraph("UE24CS352A Machine Learning Mini-Project | Team 30, Problem 50 | Reia S (PES2UG24CS921), Ritesh Babu Reddy (PES2UG24CS403)<br/>GitHub: &lt;add private repo link&gt; | Inspired by Lu, Stanford CS229 (2021)", sub),
     Paragraph("1. Problem statement", h),
     Paragraph("Resale prices of collectible merchandise (trading cards, vinyl and action figures, comics, LEGO sets, memorabilia) span several orders of magnitude and depend on "
               "rarity, condition, age and demand. We build and compare machine-learning models that <b>predict the dollar resale price</b> of a listing from its attributes, "
               "so that sellers can price items sensibly when comparable transactions are scarce. The reference CS229 report classifies Funko Pops into price bins; we "
               "generalise to six product categories and to continuous price regression.", body),
     Paragraph("2. Dataset", h),
     Paragraph(f"<b>Important:</b> no licensed real-market data was available, so we use a <b>synthetic dataset of {M['n']:,} listings</b> generated from a latent log-linear price model "
               "with a condition x rarity interaction, a vintage premium that grows with rarity, and heavy-tailed noise (occasional 'grail' outliers). Features: product type, franchise, "
               "condition (4 ordered levels), rarity (4 ordered levels), age in years, edition size, search volume, graded flag, original-packaging flag. Prices range from about $10 to $31,000 "
               "(median $136). <b>Because the generator is largely log-linear, linear models are favoured by construction; results describe the methods, not the real market.</b> The code accepts a real CSV with the same columns.", note),
     Image("results/data_overview.png", width=118*mm, height=118*mm*3.1/9),
     Paragraph("3. Approach", h),
     Paragraph("<b>Preprocessing</b> (inside each CV pipeline, so no leakage): one-hot for product type and franchise; ordinal encoding for condition and rarity; log transform for heavy-tailed edition size and "
               "search volume; standardisation for distance/linear models. <b>Target:</b> log(price), predictions mapped back with exp(). <b>Models:</b> median baseline, linear regression, ridge, "
               "kNN, RBF-SVR, decision tree, bagged trees, random forest, gradient boosting. <b>Evaluation:</b> 5-fold CV repeated 3 times; RMSE and R<super>2</super> on log price, MAE in USD, "
               "median absolute percentage error (MedAPE) and share of predictions within 25% of the true price. A hold-out split gives error by price tier and permutation importance.", body),
     Paragraph("4. Implementation overview", h),
     Paragraph("Python / scikit-learn: <font face='Courier'>features.py</font> (ColumnTransformer pipeline), <font face='Courier'>models.py</font> (model zoo wrapped in TransformedTargetRegressor), "
               "<font face='Courier'>run_experiments.py</font> (CV, tier analysis, importance, plots), <font face='Courier'>demo.py</font> (price estimate from the command line), "
               "<font face='Courier'>data/generate_synthetic.py</font>. README lists setup and run commands.", body)]
rows = [["Model", "Train RMSE", "Valid RMSE", "Valid R2", "MAE (USD)", "MedAPE", "Within 25%"]]
for n in mo:
    r = mo[n]; rows.append([n, f"{r['train']['rmse_log']:.3f}", f"{v(n,'rmse_log'):.3f}", f"{v(n,'r2_log'):.3f}", f"${v(n,'mae_usd'):.0f}", f"{v(n,'medape'):.1%}", f"{v(n,'within25'):.1%}"])
t = Table(rows, colWidths=[38*mm, 22*mm, 22*mm, 20*mm, 22*mm, 22*mm, 24*mm])
t.setStyle(TableStyle([("FONT", (0, 0), (-1, -1), "Helvetica", 7.6), ("FONT", (0, 0), (-1, 0), "Helvetica-Bold", 7.6), ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#e2e8f0")),
                       ("GRID", (0, 0), (-1, -1), 0.4, colors.HexColor("#a0aec0")), ("ALIGN", (1, 0), (-1, -1), "CENTER"), ("TOPPADDING", (0, 0), (-1, -1), 1.5), ("BOTTOMPADDING", (0, 0), (-1, -1), 1.5),
                       ("BACKGROUND", (0, 2), (-1, 3), colors.HexColor("#ebf8ff"))]))
imp = M["importance"]; top = sorted(imp, key=imp.get, reverse=True)[:3]; te = M["tier_error"]
S += [Paragraph("5. Results (validation, mean over 15 CV folds; lower RMSE is better; synthetic data)", h), t, Spacer(1, 3),
      Table([[Image("results/model_comparison.png", width=88*mm, height=88*mm*3.4/6.2), Image("results/pred_vs_actual.png", width=52*mm, height=52*mm*3.6/3.9), Image("results/feature_importance.png", width=52*mm, height=52*mm*3.4/4.6)]], colWidths=[90*mm, 54*mm, 54*mm]),
      Paragraph("6. Conclusions", h),
      Paragraph(f"&bull; <b>Every model beats the median baseline</b> (RMSE {v('Median baseline','rmse_log'):.2f} on log price). Ridge/linear regression are best (RMSE {v('Ridge','rmse_log'):.3f}, R<super>2</super> {v('Ridge','r2_log'):.2f}, "
                f"{v('Ridge','within25'):.0%} of predictions within 25%), followed by gradient boosting ({v('Gradient Boosting','rmse_log'):.3f}) and SVR ({v('SVR (RBF)','rmse_log'):.3f}). "
                "This ordering is expected because the synthetic prices are log-linear; on real data, where interactions are richer, boosting may close or reverse the gap.", bul),
      Paragraph(f"&bull; <b>Variance reduction works:</b> a single tree (RMSE {v('Decision Tree','rmse_log'):.2f}) improves to {v('Bagged Trees','rmse_log'):.2f} when bagged and {v('Random Forest','rmse_log'):.2f} as a random forest, "
                f"but trees stay behind the smooth log-linear models. kNN memorises (train RMSE 0.00) and generalises worst of the non-tree models.", bul),
      Paragraph(f"&bull; <b>Drivers of price:</b> permutation importance ranks {top[0].replace('_',' ')}, {top[1].replace('_',' ')} and {top[2].replace('_',' ')} highest, matching how the data were generated and common collecting intuition.", bul),
      Paragraph(f"&bull; <b>The most expensive items are under-priced:</b> on hold-out data the top-10% tier is predicted about {1-2.718281828**te['top 10%']['bias_log']:.0%} too low (mean log bias {te['top 10%']['bias_log']:.2f}), "
                "because rare 'grail' outliers are heavy-tailed noise that features cannot explain. Sellers should treat predictions for top-tier items as a floor, not a price.", bul),
      Paragraph("&bull; <b>Limitations / future work:</b> synthetic data; typical error is still about 30% (MedAPE). Next steps: real marketplace transactions, quantile regression for price intervals, "
                "text features from listing titles, and tuned boosting with interaction terms.", bul)]
doc.build(S)
