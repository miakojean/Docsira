export interface DossierTypeOption {
  value: string;
  label: string;
}

export interface DossierTypeGroup {
  category: string;
  options: DossierTypeOption[];
}

export const DOSSIER_TYPE_GROUPS: DossierTypeGroup[] = [
  {
    category: "1. Constitution, Vie Sociale & Restructuration",
    options: [
      { value: "CONSTITUTION", label: "Constitution de société" },
      { value: "MODIFICATION", label: "Modification statutaire" },
      { value: "DISSOLUTION", label: "Dissolution / Liquidation" },
      { value: "TRANSFORMATION", label: "Transformation de société" },
      { value: "FUSION_ACQUISITION", label: "Fusion / Acquisition (M&A)" },
      { value: "SECRETARIAT_JURIDIQUE", label: "Secrétariat juridique annuel (AGO/AGE)" },
    ],
  },
  {
    category: "2. Comptabilité, Tenue & Révision",
    options: [
      { value: "COMPTABILITE_TENUE", label: "Tenue comptable mensuelle / périodique" },
      { value: "REVISION_COMPTABLE", label: "Révision et arrêté des comptes annuels" },
      { value: "ETABLISSEMENT_ETATS_FINANCIERS", label: "Établissement des états financiers (Bilan, Compte de résultat)" },
      { value: "CONSOLIDATION_COMPTABLE", label: "Consolidation des comptes" },
      { value: "GESTION_PAIE", label: "Gestion de la paie et déclarations sociales" },
    ],
  },
  {
    category: "3. Fiscalité & Déclarations",
    options: [
      { value: "FISCALITE_ENTREPRISE", label: "Fiscalité des entreprises (Déclarations fiscales)" },
      { value: "AUDIT_FISCAL", label: "Audit et optimisation fiscale" },
      { value: "ASSISTANCE_CONTROLE_FISCAL", label: "Assistance lors d'un contrôle fiscal ou social" },
    ],
  },
  {
    category: "4. Contrats, Partenariats & Immobilier",
    options: [
      { value: "CONTRAT", label: "Rédaction et négociation de contrats" },
      { value: "PARTENARIAT", label: "Protocole d'accord / Partenariat stratégique" },
      { value: "BAIL_COMMERCIAL", label: "Bail commercial / Professionnel" },
    ],
  },
  {
    category: "5. Contentieux, Recouvrement & Procédures",
    options: [
      { value: "CONTENTIEUX", label: "Contentieux judiciaire (Affaires & Financier)" },
      { value: "ARBITRAGE_MEDIATION", label: "Arbitrage et Médiation" },
      { value: "RECOUVREMENT", label: "Recouvrement de créances et voies d'exécution" },
      { value: "PROCEDURE_COLLECTIVE", label: "Procédures collectives (Redressement / Liquidation judiciaire)" },
    ],
  },
  {
    category: "6. Conseil & Audit Global",
    options: [
      { value: "CONSEIL", label: "Conseil juridique et stratégique" },
      { value: "AUDIT_JURIDIQUE", label: "Audit juridique et d'acquisition (Due Diligence)" },
      { value: "DROIT_SOCIAL", label: "Droit social et relations de travail" },
    ],
  },
  {
    category: "7. Propriété Intellectuelle & Numérique",
    options: [
      { value: "PROPRIETE_INTELLECTUELLE", label: "Propriété intellectuelle (Marques, Brevets)" },
      { value: "CONFORMITE_RGPD", label: "Conformité réglementaire (RGPD / Protection des données)" },
    ],
  },
  {
    category: "8. Divers",
    options: [
      { value: "AUTRE", label: "Autre" },
    ],
  },
];

export const DOSSIER_TYPE_OPTIONS: DossierTypeOption[] = DOSSIER_TYPE_GROUPS.flatMap((g) => g.options);

export const DOSSIER_TYPE_LABELS: Record<string, string> = Object.fromEntries(
  DOSSIER_TYPE_OPTIONS.map((opt) => [opt.value, opt.label])
);

export function getDossierTypeLabel(typeAffair?: string | null): string {
  if (!typeAffair) return "";
  return DOSSIER_TYPE_LABELS[typeAffair] || typeAffair;
}
