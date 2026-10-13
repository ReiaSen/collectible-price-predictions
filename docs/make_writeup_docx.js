const fs = require("fs");
const { Document, Packer, Paragraph, TextRun, ImageRun, Table, TableRow, TableCell, WidthType, ShadingType, BorderStyle, AlignmentType, LevelFormat } = require("docx");
const M = JSON.parse(fs.readFileSync("results/metrics.json")); const mo = M.models;
const v = (n, k) => mo[n].valid[k];
const FONT = "Calibri", NAVY = "1A365D";
const img = (f, w, h) => new ImageRun({ type: "png", data: fs.readFileSync("results/" + f), transformation: { width: w, height: h }, altText: { title: f, description: f, name: f } });
const run = (t, o = {}) => new TextRun({ text: t, font: FONT, size: 19, ...o });
const P = (parts, o = {}) => new Paragraph({ spacing: { after: 70, line: 252 }, ...o, children: parts.map(p => typeof p === "string" ? run(p) : p) });
const H = (t) => new Paragraph({ spacing: { before: 130, after: 50 }, keepNext: true, children: [run(t, { bold: true, size: 23, color: NAVY })] });
const B = (parts) => new Paragraph({ numbering: { reference: "bul", level: 0 }, spacing: { after: 50, line: 252 }, children: parts.map(p => typeof p === "string" ? run(p) : p) });
const b = (t) => run(t, { bold: true }); const it = (t) => run(t, { italics: true }); const code = (t) => run(t, { font: "Consolas", size: 17 });

const imp = M.importance, top = Object.keys(imp).sort((a, c) => imp[c] - imp[a]).slice(0, 3).map(s => s.replace(/_/g, " "));
const topBias = M.tier_error["top 10%"].bias_log, under = Math.round((1 - Math.exp(topBias)) * 100);

const W = [2100, 1350, 1350, 1250, 1350, 1250, 1256]; // sums 9906
const cell = (t, i, head, shade) => new TableCell({ width: { size: W[i], type: WidthType.DXA }, margins: { top: 30, bottom: 30, left: 70, right: 70 },
  shading: head ? { fill: "E2E8F0", type: ShadingType.CLEAR, color: "auto" } : shade ? { fill: "EBF8FF", type: ShadingType.CLEAR, color: "auto" } : undefined,
  children: [new Paragraph({ alignment: i === 0 ? AlignmentType.LEFT : AlignmentType.CENTER, children: [run(t, { size: 17, bold: head })] })] });
const line = { style: BorderStyle.SINGLE, size: 4, color: "A0AEC0" };
const rows = [["Model", "Train RMSE", "Valid RMSE", "Valid R²", "MAE (USD)", "MedAPE", "Within 25%"]].map(r => new TableRow({ tableHeader: true, children: r.map((t, i) => cell(t, i, true)) }))
  .concat(Object.keys(mo).map(n => new TableRow({ cantSplit: true, children: [n, mo[n].train.rmse_log.toFixed(3), v(n, "rmse_log").toFixed(3), v(n, "r2_log").toFixed(3), "$" + v(n, "mae_usd").toFixed(0), (v(n, "medape") * 100).toFixed(1) + "%", (v(n, "within25") * 100).toFixed(1) + "%"]
    .map((t, i) => cell(t, i, false, n === "Ridge" || n === "Linear Regression")) })));

const noteBox = new Paragraph({ spacing: { before: 40, after: 100, line: 252 }, shading: { fill: "FFFAF0", type: ShadingType.CLEAR, color: "auto" },
  border: { top: { ...line, color: "DD6B20" }, left: { ...line, color: "DD6B20" }, bottom: { ...line, color: "DD6B20" }, right: { ...line, color: "DD6B20" } },
  children: [b("Important: "), run(`no licensed real-market data was available, so we use a `), b(`synthetic dataset of ${M.n.toLocaleString()} listings`),
    run(" generated from a latent log-linear price model with a condition × rarity interaction, a vintage premium that grows with rarity, and heavy-tailed noise (occasional “grail” outliers). Features: product type, franchise, condition (4 ordered levels), rarity (4 ordered levels), age in years, edition size, search volume, graded flag, original-packaging flag. Prices range from about $10 to $31,000 (median $136). "),
    b("Because the generator is largely log-linear, linear models are favoured by construction; results describe the methods, not the real market."), run(" The code accepts a real CSV with the same columns.")] });

const doc = new Document({
  creator: "Reia S, Ritesh Babu Reddy", title: "Collectible Merchandise Price Prediction",
  styles: { default: { document: { run: { font: FONT, size: 19 } } } },
  numbering: { config: [{ reference: "bul", levels: [{ level: 0, format: LevelFormat.BULLET, text: "•", alignment: AlignmentType.LEFT, style: { paragraph: { indent: { left: 360, hanging: 240 } } } }] }] },
  sections: [{ properties: { page: { size: { width: 11906, height: 16838 }, margin: { top: 720, bottom: 680, left: 1000, right: 1000 } } },
    children: [
      new Paragraph({ spacing: { after: 40 }, children: [run("Collectible Merchandise Price Prediction: A Machine Learning Case Study", { bold: true, size: 32 })] }),
      P([run("UE24CS352A Machine Learning Mini-Project  |  Team 30, Problem 50  |  Reia S (PES2UG24CS921), Ritesh Babu Reddy (PES2UG24CS403)", { color: "4A5568", size: 17 })], { spacing: { after: 10 } }),
      P([run("GitHub: <add private repo link>  |  Inspired by Lu, Stanford CS229 (2021)", { color: "4A5568", size: 17 })]),
      H("1. Problem statement"),
      P(["Resale prices of collectible merchandise (trading cards, vinyl and action figures, comics, LEGO sets, memorabilia) span several orders of magnitude and depend on rarity, condition, age and demand. We build and compare machine-learning models that ", b("predict the dollar resale price"), " of a listing from its attributes, so that sellers can price items sensibly when comparable transactions are scarce. The reference CS229 report classifies Funko Pops into price bins; we generalise to six product categories and to continuous price regression."]),
      H("2. Dataset"), noteBox,
      new Paragraph({ alignment: AlignmentType.CENTER, spacing: { after: 40 }, children: [img("data_overview.png", 420, 145)] }),
      H("3. Approach"),
      P([b("Preprocessing"), " (inside each CV pipeline, so no leakage): one-hot for product type and franchise; ordinal encoding for condition and rarity; log transform for heavy-tailed edition size and search volume; standardisation for distance/linear models. ", b("Target: "), "log(price), predictions mapped back with exp(). ", b("Models: "), "median baseline, linear regression, ridge, kNN, RBF-SVR, decision tree, bagged trees, random forest, gradient boosting. ", b("Evaluation: "), "5-fold CV repeated 3 times; RMSE and R² on log price, MAE in USD, median absolute percentage error (MedAPE) and the share of predictions within 25% of the true price. A hold-out split gives error by price tier and permutation importance."]),
      H("4. Implementation overview"),
      P(["Python / scikit-learn: ", code("features.py"), " (ColumnTransformer pipeline), ", code("models.py"), " (model zoo wrapped in TransformedTargetRegressor), ", code("run_experiments.py"), " (CV, tier analysis, importance, plots), ", code("demo.py"), " (price estimate from the command line), ", code("data/generate_synthetic.py"), ". The README lists setup and run commands."]),
      H("5. Results (validation, mean over 15 CV folds; lower RMSE is better; synthetic data)"),
      new Table({ width: { size: 9906, type: WidthType.DXA }, columnWidths: W, rows,
        borders: { top: line, bottom: line, left: line, right: line, insideHorizontal: line, insideVertical: line } }),
      new Paragraph({ spacing: { before: 80, after: 40 }, alignment: AlignmentType.CENTER, children: [img("model_comparison.png", 270, 148), run("  "), img("pred_vs_actual.png", 165, 152), run("  "), img("feature_importance.png", 190, 140)] }),
      H("6. Conclusions"),
      B([b("Every model beats the median baseline"), ` (RMSE ${v("Median baseline", "rmse_log").toFixed(2)} on log price). Ridge/linear regression are best (RMSE ${v("Ridge", "rmse_log").toFixed(3)}, R² ${v("Ridge", "r2_log").toFixed(2)}, ${(v("Ridge", "within25") * 100).toFixed(0)}% of predictions within 25%), followed by gradient boosting (${v("Gradient Boosting", "rmse_log").toFixed(3)}) and SVR (${v("SVR (RBF)", "rmse_log").toFixed(3)}). This ordering is expected because the synthetic prices are log-linear; on real data, where interactions are richer, boosting may close or reverse the gap.`]),
      B([b("Variance reduction works:"), ` a single tree (RMSE ${v("Decision Tree", "rmse_log").toFixed(2)}) improves to ${v("Bagged Trees", "rmse_log").toFixed(2)} when bagged and ${v("Random Forest", "rmse_log").toFixed(2)} as a random forest, but trees stay behind the smooth log-linear models. kNN memorises (train RMSE 0.00) and generalises worst of the non-tree models.`]),
      B([b("Drivers of price:"), ` permutation importance ranks ${top[0]}, ${top[1]} and ${top[2]} highest, matching how the data were generated and common collecting intuition.`]),
      B([b("The most expensive items are under-priced:"), ` on hold-out data the top-10% tier is predicted about ${under}% too low (mean log bias ${topBias.toFixed(2)}), because rare “grail” outliers are heavy-tailed noise that the features cannot explain. Sellers should treat predictions for top-tier items as a floor, not a price.`]),
      B([b("Limitations / future work:"), " synthetic data; typical error is still about 30% (MedAPE). Next steps: real marketplace transactions, quantile regression for price intervals, text features from listing titles, and tuned boosting with interaction terms."]),
    ] }] });
Packer.toBuffer(doc).then(buf => { fs.writeFileSync("docs/Team30_Problem50_Writeup.docx", buf); console.log("written"); });
