#!/usr/bin/env python3
"""Make compact efficiency/fake-rate/score plots from harvested ParT DQM."""

import argparse
import os
import ROOT

ROOT.gROOT.SetBatch(True)
ROOT.gStyle.SetOptStat(0)


def get_hist(root_file, path):
    hist = root_file.Get(path)
    if not hist:
        raise RuntimeError("Missing histogram: {}".format(path))
    return hist


def ratio(numerator, denominator, name):
    result = numerator.Clone(name)
    result.SetDirectory(0)
    result.Divide(numerator, denominator, 1.0, 1.0, "B")
    return result


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("dqm_file", help="Harvested DQM ROOT file")
    parser.add_argument("--folder", default="DQMData/Run 1/HLT/Run summary/Tau/TauValidation/PFPuppiParT",
                        help="Folder containing the ParT validation histograms")
    parser.add_argument("--hps-file", help="Optional harvested DQM file containing HPS + DeepTau histograms")
    parser.add_argument("--hps-folder", default="DQMData/Run 1/HLT/Run summary/Tau/TauValidation",
                        help="HPS DQM folder (may include a CutWP_* or CutID_* selection)")
    parser.add_argument("--output", default="TauValidationPlots/PFPuppiParT",
                        help="Output directory for PDF plots")
    args = parser.parse_args()

    root_file = ROOT.TFile.Open(args.dqm_file)
    if not root_file or root_file.IsZombie():
        raise RuntimeError("Cannot open DQM file: {}".format(args.dqm_file))
    hps_file = ROOT.TFile.Open(args.hps_file) if args.hps_file else None
    if args.hps_file and (not hps_file or hps_file.IsZombie()):
        raise RuntimeError("Cannot open HPS DQM file: {}".format(args.hps_file))
    os.makedirs(args.output, exist_ok=True)
    thresholds = [
        ("", "PR WP (0.11645)"),
        ("/Score0p00", "score > 0.00"),
        ("/Score0p05", "score > 0.05"),
        ("/Score0p10", "score > 0.10"),
        ("/Score0p11645", "score > 0.11645"),
        ("/Score0p15", "score > 0.15"),
        ("/Score0p20", "score > 0.20"),
    ]
    colors = [ROOT.kBlack, ROOT.kGray + 2, ROOT.kBlue, ROOT.kAzure + 7,
              ROOT.kRed, ROOT.kGreen + 2, ROOT.kMagenta]

    for metric in ("efficiency", "fake_rate"):
        for variable, title, axis in (("pt", "vs p_{T}", "p_{T} [GeV]"),
                                      ("eta", "vs #eta", "#eta")):
            canvas = ROOT.TCanvas("{}_{}".format(metric, variable), title, 900, 700)
            legend = ROOT.TLegend(0.58, 0.18, 0.88, 0.42)
            curves = []
            for (suffix, label), color in zip(thresholds, colors):
                base = args.folder + suffix
                if metric == "efficiency":
                    numerator = get_hist(root_file, base + "/genTauMatched_" + variable)
                    denominator = get_hist(root_file, base + "/genTau_" + variable)
                    ytitle = "Efficiency"
                else:
                    numerator = get_hist(root_file, base + "/fakeJet_" + variable)
                    denominator = get_hist(root_file, base + "/recoJet_" + variable)
                    ytitle = "Fake fraction"
                h = ratio(numerator, denominator, "{}_{}_{}".format(metric, variable, len(curves)))
                h.SetTitle("{} {} ;{};{}".format("Tau efficiency" if metric == "efficiency" else "Jet fake fraction", title, axis, ytitle))
                h.SetLineColor(color)
                h.SetLineWidth(2)
                h.SetMinimum(0.0)
                h.SetMaximum(1.05)
                curves.append(h)
                legend.AddEntry(h, label, "l")
            if hps_file:
                hps_base = args.hps_folder
                if metric == "efficiency":
                    hps_num = get_hist(hps_file, hps_base + "/genTauMatched_" + variable)
                    hps_den = get_hist(hps_file, hps_base + "/genTau_" + variable)
                    hps_ratio = ratio(hps_num, hps_den, "hps_{}_{}".format(metric, variable))
                else:
                    hps_den = get_hist(hps_file, hps_base + "/recoTau_" + variable)
                    hps_matched = get_hist(hps_file, hps_base + "/recoTauMatched_" + variable)
                    hps_num = hps_den.Clone("hps_fake_numerator_{}_{}".format(variable, metric))
                    hps_num.Add(hps_matched, -1.0)
                    hps_ratio = ratio(hps_num, hps_den, "hps_{}_{}".format(metric, variable))
                hps_ratio.SetTitle("{} {};{};{}".format("Tau efficiency" if metric == "efficiency" else "Jet fake fraction", title, axis, ytitle))
                hps_ratio.SetLineColor(ROOT.kBlack)
                hps_ratio.SetLineStyle(2)
                hps_ratio.SetLineWidth(3)
                curves.append(hps_ratio)
                legend.AddEntry(hps_ratio, "HPS + DeepTau", "l")
            for i, h in enumerate(curves):
                h.Draw("E1" if i == 0 else "E1 SAME")
            legend.Draw()
            canvas.SaveAs(os.path.join(args.output, "{}_vs_{}.pdf".format(metric, variable)))

    # The matched and fake score distributions come from the nominal WP module.
    nominal = args.folder
    score_canvas = ROOT.TCanvas("score", "ParT score", 900, 700)
    matched = get_hist(root_file, nominal + "/recoJetMatched_score")
    fake = get_hist(root_file, nominal + "/fakeJet_score")
    matched.SetLineColor(ROOT.kBlue + 1)
    fake.SetLineColor(ROOT.kRed + 1)
    matched.SetLineWidth(2)
    fake.SetLineWidth(2)
    matched.SetTitle("ParT score;TauvsAll score;Jets")
    matched.Draw("HIST")
    fake.Draw("HIST SAME")
    legend = ROOT.TLegend(0.58, 0.75, 0.88, 0.88)
    legend.AddEntry(matched, "Matched to gen visible tau", "l")
    legend.AddEntry(fake, "Unmatched selected jet", "l")
    legend.Draw()
    score_canvas.SaveAs(os.path.join(args.output, "part_score.pdf"))

    path_den = get_hist(root_file, nominal + "/pathDenominator")
    path_num = get_hist(root_file, nominal + "/pathAccepted")
    n_den = path_den.GetBinContent(1)
    n_num = path_num.GetBinContent(1)
    path_eff = n_num / n_den if n_den else 0.0
    print("Double-tau HLT path efficiency: {:.5f} ({:.0f}/{:.0f})".format(path_eff, n_num, n_den))

    # Decay-mode efficiency uses the generated tau's mode, since the HLT jet
    # candidate has no reconstructed tau decay-mode label.
    dm_folder = nominal + "/GenDecayModes"
    dms = ("oneProng0Pi0", "oneProng1Pi0", "oneProng2Pi0", "oneProngOther",
           "threeProng0Pi0", "threeProng1Pi0", "threeProngOther")
    canvas = ROOT.TCanvas("dm_eff", "Efficiency by generated tau decay mode", 900, 700)
    legend = ROOT.TLegend(0.62, 0.54, 0.89, 0.88)
    curves = []
    for i, dm in enumerate(dms):
        h = ratio(get_hist(root_file, dm_folder + "/genTauMatched_" + dm + "_pt"),
                  get_hist(root_file, dm_folder + "/genTau_" + dm + "_pt"), "dm_" + dm)
        h.SetTitle("PFPuppi+ParT efficiency by generated decay mode;p_{T}^{gen} [GeV];Efficiency")
        h.SetLineColor(ROOT.TColor.GetColorPalette(i * 5))
        h.SetLineWidth(2)
        h.SetMinimum(0.0)
        h.SetMaximum(1.05)
        curves.append(h)
        legend.AddEntry(h, dm, "l")
    for i, h in enumerate(curves):
        h.Draw("E1" if i == 0 else "E1 SAME")
    legend.Draw()
    canvas.SaveAs(os.path.join(args.output, "efficiency_by_gen_decay_mode.pdf"))
    root_file.Close()
    if hps_file:
        hps_file.Close()


if __name__ == "__main__":
    main()
