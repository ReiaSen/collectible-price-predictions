const pptxgen = require("pptxgenjs");
const { applyTheme } = require("/mnt/skills/public/pptx/scripts/apply_theme.js");
const M = require(process.cwd() + "/results/metrics.json"); const mo = M.models;
const THEME = { name: "Collectibles ML", headFontFace: "Calibri", bodyFontFace: "Calibri",
  colors: { dk1: "1A202C", lt1: "FFFFFF", dk2: "1A365D", lt2: "EDF2F7", accent1: "2B6CB0", accent2: "DD6B20", accent3: "A0AEC0", accent4: "38A169", accent5: "805AD5", accent6: "E53E3E", hlink: "2B6CB0", folHlink: "805AD5" } };
const pres = new pptxgen(); pres.layout = "LAYOUT_16x9"; pres.theme = { headFontFace: "Calibri", bodyFontFace: "Calibri" };
pres.title = "Collectible Merchandise Price Prediction - Team 30";
pres.defineSlideMaster({ title: "TITLE_ONLY", background: { color: "FFFFFF" }, objects: [{ rect: { x: 0, y: 0, w: 10, h: 0.95, fill: { color: "1A365D" } } }], slideNumber: { x: 9.2, y: 5.25, color: "A0AEC0", fontSize: 10 } });
pres.defineSlideMaster({ title: "DARK", background: { color: "1A365D" } });
const content = (t) => { const s = pres.addSlide({ masterName: "TITLE_ONLY" }); s.addText(t, { x: 0.5, y: 0.12, w: 9, h: 0.7, fontSize: 26, bold: true, color: "FFFFFF", valign: "middle", margin: 0, isTextBox: true, objectName: "Title" }); return s; };
const bullets = (s, items, o = {}) => s.addText(items.map((t, i) => ({ text: t, options: { bullet: true, breakLine: i < items.length - 1, paraSpaceAfter: 8 } })), Object.assign({ x: 0.5, y: 1.25, w: 9, h: 3.8, fontSize: 18, color: "1A202C", valign: "top", isTextBox: true }, o));
const v = (n, k) => mo[n].valid[k];

let s = pres.addSlide({ masterName: "DARK" });
s.addText("Collectible Merchandise Price Prediction", { x: 0.7, y: 1.1, w: 8.6, h: 1.2, fontSize: 38, bold: true, color: "FFFFFF", isTextBox: true });
s.addText("A machine-learning case study: predicting the resale price of trading cards, figures, comics, LEGO sets and memorabilia", { x: 0.7, y: 2.5, w: 8.6, h: 0.9, fontSize: 18, color: "EDF2F7", isTextBox: true });
s.addText("UE24CS352A Machine Learning | Team 30 | Problem 50\nReia S (PES2UG24CS921) and Ritesh Babu Reddy (PES2UG24CS403)", { x: 0.7, y: 4.1, w: 8.6, h: 0.9, fontSize: 14, color: "A0AEC0", isTextBox: true });
s.addNotes("Introduce the team and problem 50. We generalise the Funko-only CS229 reference report to six collectible categories and to dollar-price regression.");

s = content("Problem: what should this item sell for?");
bullets(s, ["Collectible prices span $10 to $30,000+ and depend on rarity, condition, age and demand", "Task: predict the dollar resale price of a listing from its attributes", "Useful when comparable transactions are scarce (new or unusual items)", "Challenges: right-skewed prices, mixed feature types, rare 'grail' outliers", "Reference: Lu (CS229, 2021) classified Funko Pop price bins; we generalise to six categories and regression"]);

s = content("Dataset (synthetic, 1,200 listings)");
s.addImage({ path: "results/data_overview.png", x: 0.4, y: 1.15, w: 5.6, h: 5.6 * 3.1 / 9, altText: "Price histogram and log price histogram" });
s.addText("9 features: product type, franchise, condition, rarity, age, edition size, search volume, graded, original packaging", { x: 0.5, y: 3.9, w: 5.5, h: 0.9, fontSize: 13, color: "4A5568", isTextBox: true });
s.addText("Why synthetic?", { x: 6.3, y: 1.15, w: 3.3, h: 0.4, fontSize: 16, bold: true, color: "DD6B20", isTextBox: true });
s.addText("No licensed real-market data was available. Prices come from a latent log-linear model with a condition x rarity interaction, a vintage premium and heavy-tailed noise.\n\nLinear models are favoured by construction, so results describe the methods, not the real market.", { x: 6.3, y: 1.55, w: 3.3, h: 3.4, fontSize: 13, color: "1A202C", valign: "top", isTextBox: true });
s.addNotes("Be upfront that the data is synthetic. Code accepts a real CSV with the same columns.");

s = content("Approach");
[["Preprocess", "One-hot, ordinal and log transforms inside each CV pipeline (no leakage)"], ["Target", "Predict log(price), map back with exp(): fits skewed prices"], ["Models", "Baseline, linear, ridge, kNN, SVR, tree, bagging, forest, boosting"], ["Evaluate", "5-fold CV x3; RMSE, R2, MAE, MedAPE, within-25% hit rate"]].forEach((c, i) => { const x = 0.5 + i * 2.28;
  s.addShape(pres.ShapeType.rect, { x, y: 1.3, w: 2.1, h: 2.7, fill: { color: "EDF2F7" }, line: { color: "A0AEC0", width: 0.75 }, objectName: "card" + i });
  s.addText(c[0], { x: x + 0.1, y: 1.4, w: 1.9, h: 0.5, fontSize: 18, bold: true, color: "2B6CB0", isTextBox: true });
  s.addText(c[1], { x: x + 0.1, y: 1.95, w: 1.9, h: 1.95, fontSize: 14, color: "1A202C", valign: "top", isTextBox: true }); });

s = content("Models compared");
const T = (t, b) => ({ text: t, options: { bold: !!b, fontSize: 13, color: b ? "FFFFFF" : "1A202C", fill: { color: b ? "2B6CB0" : "FFFFFF" } } });
s.addTable([[T("Family", 1), T("Models", 1), T("Why include it", 1)],
  [T("Baseline"), T("Median"), T("Floor to beat")], [T("Linear"), T("Linear, Ridge"), T("Interpretable; natural for log prices")], [T("Kernel / instance"), T("RBF-SVR, kNN"), T("Non-linear, similarity-based")],
  [T("Trees"), T("Decision tree, Bagging, Random Forest"), T("Handle interactions; bagging cuts variance")], [T("Boosting"), T("Gradient Boosting"), T("Usually strongest on tabular data")]],
  { x: 0.5, y: 1.3, w: 9, colW: [2.0, 3.4, 3.6], border: { type: "solid", color: "A0AEC0", pt: 0.75 }, rowH: 0.5 });

s = content("Results: validation error by model");
s.addImage({ path: "results/model_comparison.png", x: 0.4, y: 1.1, w: 5.6, h: 5.6 * 3.4 / 6.2, altText: "Train vs validation RMSE by model" });
bullets(s, [`Ridge best: RMSE ${v("Ridge", "rmse_log").toFixed(3)}, R2 ${v("Ridge", "r2_log").toFixed(2)}`, `${(v("Ridge", "within25") * 100).toFixed(0)}% of predictions within 25% of true price`, `Gradient boosting close behind (${v("Gradient Boosting", "rmse_log").toFixed(3)})`, `Median baseline: ${v("Median baseline", "rmse_log").toFixed(2)}`],
  { x: 6.2, y: 1.3, w: 3.4, h: 3.5, fontSize: 15 });
s.addNotes("Linear models win partly because the synthetic generator is log-linear. Say so if asked.");

s = content("Trees: variance reduction helps");
bullets(s, [`Single decision tree: RMSE ${v("Decision Tree", "rmse_log").toFixed(2)}`, `Bagged trees: ${v("Bagged Trees", "rmse_log").toFixed(2)}`, `Random forest: ${v("Random Forest", "rmse_log").toFixed(2)}`, "Trees still trail smooth log-linear models on this data", `kNN memorises: train RMSE 0.00 vs validation ${v("kNN (k=10)", "rmse_log").toFixed(2)}`]);

s = content("What drives price, and where the model fails");
s.addImage({ path: "results/feature_importance.png", x: 0.4, y: 1.1, w: 4.4, h: 4.4 * 3.4 / 4.6, altText: "Permutation importance" });
s.addImage({ path: "results/pred_vs_actual.png", x: 5.1, y: 1.1, w: 3.6, h: 3.6 * 3.6 / 3.9, altText: "Predicted vs actual price" });
s.addText(`Rarity, product type and edition size matter most. Top-10% items are under-predicted by about ${Math.round((1 - Math.exp(M.tier_error["top 10%"].bias_log)) * 100)}%: treat top-tier estimates as a floor.`, { x: 0.5, y: 4.55, w: 9, h: 0.6, fontSize: 14, color: "1A202C", isTextBox: true });

s = content("Conclusions and future work");
bullets(s, ["All models beat the median baseline; Ridge best with about 30% median error", "Bagging and forests tame tree overfitting but trail log-linear models here", "Predictions for rare, expensive items are biased low: heavy-tailed outliers", "Next: real marketplace data, quantile regression for price ranges, listing-title text features, tuned boosting"]);

s = content("Live demo and repository");
s.addText("python src/demo.py --rarity ultra_rare --condition mint \\\n    --graded 1 --age_years 25 --edition_size 5000 --search_volume 2000", { x: 0.5, y: 1.3, w: 9, h: 0.9, fontSize: 14, fontFace: "Consolas", color: "FFFFFF", fill: { color: "1A202C" }, margin: 10, isTextBox: true });
bullets(s, ["Prints price estimates from Ridge, Gradient Boosting and Random Forest", "python src/run_experiments.py regenerates all metrics and figures", "Private GitHub repo with README, shared with faculty and TAs"], { y: 2.5, h: 2.5, fontSize: 16 });
(async () => { await pres.writeFile({ fileName: "Team30_Problem50_Slides.pptx" }); await applyTheme("Team30_Problem50_Slides.pptx", THEME); console.log("done"); })();
