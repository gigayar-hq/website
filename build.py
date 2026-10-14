"""Builds the Gigayar website into docs/ (served as-is by GitHub Pages).

    python build.py                       # rebuild docs/
    python build.py --sync-legal PATH     # first copy the app's legal texts from PATH, then rebuild

PATH is the Nyongo app's assets/legal folder, e.g. ../nyongo_app/nyongo_manager/assets/legal.
Standard library only. Every page exists in English (/) and French (/fr/).
"""

import argparse
import html
import re
import shutil
from datetime import date
from pathlib import Path

ROOT = Path(__file__).parent
OUT = ROOT / "docs"
LEGAL = ROOT / "content" / "legal" / "nyongo"
DOMAIN = "https://gigayar.com"
SUPPORT = "support@gigayar.com"
LANGS = ("en", "fr")


# --------------------------------------------------------------------------- icons (Lucide, ISC)

ICONS = {
    "users": '<path d="M16 21v-2a4 4 0 0 0-4-4H6a4 4 0 0 0-4 4v2"/><circle cx="9" cy="7" r="4"/>'
    '<path d="M22 21v-2a4 4 0 0 0-3-3.87"/><path d="M16 3.13a4 4 0 0 1 0 7.75"/>',
    "bell": '<path d="M6 8a6 6 0 0 1 12 0c0 7 3 9 3 9H3s3-2 3-9"/><path d="M10.3 21a1.94 1.94 0 0 0 3.4 0"/>',
    "shield": '<path d="M20 13c0 5-3.5 7.5-7.66 8.95a1 1 0 0 1-.67-.01C7.5 20.5 4 18 4 13V6a1 1 0 0 1 1-1'
    'c2 0 4.5-1.2 6.24-2.72a1.17 1.17 0 0 1 1.52 0C14.51 3.81 17 5 19 5a1 1 0 0 1 1 1z"/><path d="m9 12 2 2 4-4"/>',
    "chat": '<path d="M7.9 20A9 9 0 1 0 4 16.1L2 22Z"/>',
    "gauge": '<path d="m12 14 4-4"/><path d="M3.34 19a10 10 0 1 1 17.32 0"/>',
    "globe": '<circle cx="12" cy="12" r="10"/><path d="M12 2a14.5 14.5 0 0 0 0 20 14.5 14.5 0 0 0 0-20"/>'
    '<path d="M2 12h20"/>',
    "wallet": '<path d="M19 7V4a1 1 0 0 0-1-1H5a2 2 0 0 0 0 4h15a1 1 0 0 1 1 1v4h-3a2 2 0 0 0 0 4h3'
    'a1 1 0 0 0 1-1v-2a1 1 0 0 0-1-1"/><path d="M3 5v14a2 2 0 0 0 2 2h15a1 1 0 0 0 1-1v-4"/>',
    "bulb": '<path d="M15 14c.2-1 .7-1.7 1.5-2.5 1-.9 1.5-2.2 1.5-3.5A6 6 0 0 0 6 8c0 1 .2 2.2 1.5 3.5'
    '.7.7 1.3 1.5 1.5 2.5"/><path d="M9 18h6"/><path d="M10 22h4"/>',
    "eye": '<path d="M2.06 12.35a1 1 0 0 1 0-.7 10.75 10.75 0 0 1 19.88 0 1 1 0 0 1 0 .7 10.75 10.75 0 0 1-19.88 0"/>'
    '<circle cx="12" cy="12" r="3"/>',
    "lock": '<rect width="18" height="11" x="3" y="11" rx="2" ry="2"/><path d="M7 11V7a5 5 0 0 1 10 0v4"/>',
}


def icon(name, size=22):
    return (
        f'<svg width="{size}" height="{size}" viewBox="0 0 24 24" fill="none" stroke="currentColor" '
        f'stroke-width="2" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true">{ICONS[name]}</svg>'
    )


# --------------------------------------------------------------------------- text

T = {
    "en": {
        "skip": "Skip to content",
        "nav_contact": "Contact",
        "lang_switch": "FR",
        "lang_switch_label": "Version française",
        "footer_tag": "Technology for everyday life.",
        "privacy": "Privacy policy",
        "terms": "Terms of use",
        "delete": "Delete your account",
        "support": "Support",
        # home
        "home_title": "Gigayar · Technology for everyday life",
        "home_desc": "Gigayar builds simple, honest tools for everyday life. Our first product is Nyongo, "
        "a personal tracker for money lent and borrowed.",
        "home_h1": "Technology for everyday life.",
        "home_lead": "Gigayar builds simple, honest tools for the situations people find awkward, stressful or "
        "hard to manage, starting with money between friends and family.",
        "home_cta": "Discover Nyongo",
        "home_cta2": "Contact us",
        "products_eyebrow": "Products",
        "products_title": "What we are building",
        "nyongo_tag": "First product · Android, coming soon",
        "nyongo_card": "Keep track of money you lend and borrow. Nyongo sends the reminders for you, "
        "so you don't have to ask.",
        "learn_more": "Learn more →",
        "soon_tag": "Coming next",
        "soon_title": "More to come",
        "soon_text": "Gigayar is just getting started. New products will appear here.",
        "principles_eyebrow": "How we work",
        "principles_title": "Three rules for everything we make",
        "p1_t": "Useful first",
        "p1": "We start from real situations in people's lives, not from technology looking for a use.",
        "p2_t": "Honest by design",
        "p2": "Clear about what our products do and don't do. No hidden costs, no tricks.",
        "p3_t": "Your data is yours",
        "p3": "We collect only what a product needs to work. We don't sell data or use it for advertising.",
        "contact_title": "Get in touch",
        "contact_text": "Questions, feedback or ideas? Write to us.",
        # nyongo
        "n_title": "Nyongo · Track money lent and borrowed",
        "n_desc": "Record who owes you and who you owe. Nyongo reminds the other person for you. "
        "No money moves through the app.",
        "n_by": "by Gigayar",
        "n_slogan": "Don't let them borrow on their terms.",
        "n_lead": "Record who owes you and who you owe. Nyongo reminds the other person for you, "
        "so you never have to start the awkward conversation.",
        "n_status": "Coming soon on Google Play",
        "n_beta": "Test it early",
        "n_beta_subject": "Nyongo beta",
        "n_features_eyebrow": "Features",
        "n_features_title": "Everything you need, nothing awkward",
        "f": [
            ("users", "Everyone in one place",
             "One list of the people you deal with, and the balance between you at a glance."),
            ("bell", "Reminders sent for you",
             "Choose how often. Nyongo reminds the other person by notification or email, so you don't have to."),
            ("shield", "Shared and confirmed",
             "If they use Nyongo too, they confirm the debt and every payment. No more “I already paid you”."),
            ("chat", "Talk it through",
             "A chat with each person, right next to your shared history: extensions, changes, payments."),
            ("gauge", "Stay within your limits",
             "Set a monthly limit for lending and borrowing, and see where you stand."),
            ("globe", "English and French",
             "Nyongo speaks your language, with dates and amounts in your local format."),
        ],
        "n_money_title": "No money moves through Nyongo",
        "n_money": "Nyongo is a tool for keeping records and sending reminders. It never holds, sends or receives "
        "money, and never asks for bank or card details. You pay each other however you like, outside the app.",
        "n_how_eyebrow": "How it works",
        "n_how_title": "Three steps",
        "s": [
            ("Record a debt", "The amount, the person, the due date. It takes a few seconds."),
            ("Share it or keep it private",
             "Send it to their Nyongo account to confirm, or keep it as your own note."),
            ("Let Nyongo remind them", "On the schedule you choose, until it's settled."),
        ],
        "n_more_title": "Help and legal",
        # delete account
        "d_title": "Delete your Nyongo account",
        "d_desc": "How to delete your Nyongo account and what happens to your data.",
        "d_intro": "Nyongo is made by Gigayar. You can delete your account and your data at any time.",
        "d_app_h": "In the app",
        "d_app": [
            "Open Nyongo and sign in.",
            "Go to <strong>Profile</strong>.",
            "Tap <strong>Delete my account</strong>.",
            "Enter your password, then tap <strong>Delete permanently</strong>.",
        ],
        "d_noapp_h": "Without the app",
        "d_noapp": "If you can no longer use the app, email <a href=\"mailto:{support}?subject=Delete%20my%20account\">"
        "{support}</a> from the email address of your account, with the subject “Delete my account”. "
        "We will reply to confirm once your account is deleted.",
        "d_gone_h": "What is deleted",
        "d_gone": [
            "Your account: name, email address, phone number and password.",
            "Your private records and the contacts you added.",
            "Your messages.",
            "Requests you sent that were never answered.",
            "Your phone's notification token.",
        ],
        "d_kept_h": "What is kept",
        "d_kept": "Debts you shared with other people, and that they accepted, stay in their records as their own "
        "private notes, because they are part of their history too. They keep your name as it appeared on the "
        "debt, are no longer linked to any account, and no reminders are sent about them.",
        "d_more": "Read the <a href=\"{privacy}\">Privacy policy</a> for more about how Nyongo handles your data.",
        # 404
        "nf_title": "Page not found",
        "nf_text": "This page doesn't exist or has moved.",
        "nf_home": "Back to the home page",
    },
    "fr": {
        "skip": "Aller au contenu",
        "nav_contact": "Contact",
        "lang_switch": "EN",
        "lang_switch_label": "English version",
        "footer_tag": "La technologie au service du quotidien.",
        "privacy": "Politique de confidentialité",
        "terms": "Conditions d'utilisation",
        "delete": "Supprimer votre compte",
        "support": "Assistance",
        # home
        "home_title": "Gigayar · La technologie au service du quotidien",
        "home_desc": "Gigayar conçoit des outils simples et honnêtes pour le quotidien. Notre premier produit est "
        "Nyongo, un suivi personnel de l'argent prêté et emprunté.",
        "home_h1": "La technologie au service du quotidien.",
        "home_lead": "Gigayar conçoit des outils simples et honnêtes pour les situations que l'on trouve gênantes, "
        "stressantes ou difficiles à gérer, à commencer par l'argent entre amis et en famille.",
        "home_cta": "Découvrir Nyongo",
        "home_cta2": "Nous écrire",
        "products_eyebrow": "Produits",
        "products_title": "Ce que nous construisons",
        "nyongo_tag": "Premier produit · Android, bientôt disponible",
        "nyongo_card": "Suivez l'argent que vous prêtez et empruntez. Nyongo envoie les rappels à votre place, "
        "pour que vous n'ayez pas à demander.",
        "learn_more": "En savoir plus →",
        "soon_tag": "Prochainement",
        "soon_title": "D'autres à venir",
        "soon_text": "Gigayar ne fait que commencer. Les prochains produits apparaîtront ici.",
        "principles_eyebrow": "Notre façon de faire",
        "principles_title": "Trois règles pour tout ce que nous créons",
        "p1_t": "L'utilité d'abord",
        "p1": "Nous partons de situations réelles de la vie des gens, pas d'une technologie qui cherche une utilité.",
        "p2_t": "Honnêtes par principe",
        "p2": "Clairs sur ce que nos produits font et ne font pas. Pas de coûts cachés, pas de pièges.",
        "p3_t": "Vos données vous appartiennent",
        "p3": "Nous ne collectons que ce dont un produit a besoin pour fonctionner. Nous ne vendons pas les données "
        "et ne les utilisons pas pour la publicité.",
        "contact_title": "Nous contacter",
        "contact_text": "Une question, un avis, une idée&nbsp;? Écrivez-nous.",
        # nyongo
        "n_title": "Nyongo · Suivez l'argent prêté et emprunté",
        "n_desc": "Notez qui vous doit et à qui vous devez. Nyongo relance l'autre personne pour vous. "
        "Aucun argent ne passe par l'application.",
        "n_by": "par Gigayar",
        "n_slogan": "Ne les laissez pas emprunter à leurs conditions.",
        "n_lead": "Notez qui vous doit de l'argent et à qui vous en devez. Nyongo relance l'autre personne pour vous, "
        "pour vous éviter la conversation gênante.",
        "n_status": "Bientôt sur Google Play",
        "n_beta": "Le tester en avant-première",
        "n_beta_subject": "Bêta Nyongo",
        "n_features_eyebrow": "Fonctionnalités",
        "n_features_title": "Tout ce qu'il faut, sans la gêne",
        "f": [
            ("users", "Tout le monde au même endroit",
             "Une liste des personnes avec qui vous êtes en compte, et le solde entre vous en un coup d'œil."),
            ("bell", "Des rappels envoyés pour vous",
             "Choisissez la fréquence. Nyongo relance l'autre personne par notification ou par e-mail, "
             "pour que vous n'ayez pas à le faire."),
            ("shield", "Partagé et confirmé",
             "Si l'autre personne utilise aussi Nyongo, elle confirme la dette et chaque paiement. "
             "Fini les «&nbsp;je t'ai déjà remboursé&nbsp;»."),
            ("chat", "En parler",
             "Une discussion avec chaque personne, juste à côté de votre historique commun&nbsp;: délais, "
             "modifications, paiements."),
            ("gauge", "Rester dans vos limites",
             "Fixez une limite mensuelle pour vos prêts et vos emprunts, et voyez où vous en êtes."),
            ("globe", "En français et en anglais",
             "Nyongo parle votre langue, avec les dates et les montants au format local."),
        ],
        "n_money_title": "Aucun argent ne passe par Nyongo",
        "n_money": "Nyongo sert à garder une trace et à envoyer des rappels. L'application ne détient, n'envoie ni ne "
        "reçoit jamais d'argent, et ne demande jamais de coordonnées bancaires. Vous vous payez comme vous le "
        "souhaitez, en dehors de l'application.",
        "n_how_eyebrow": "Comment ça marche",
        "n_how_title": "Trois étapes",
        "s": [
            ("Notez une dette", "Le montant, la personne, la date d'échéance. Quelques secondes suffisent."),
            ("Partagez-la ou gardez-la pour vous",
             "Envoyez-la sur son compte Nyongo pour qu'elle la confirme, ou gardez-la comme note personnelle."),
            ("Laissez Nyongo relancer", "Au rythme que vous choisissez, jusqu'à ce que ce soit réglé."),
        ],
        "n_more_title": "Aide et informations légales",
        # delete account
        "d_title": "Supprimer votre compte Nyongo",
        "d_desc": "Comment supprimer votre compte Nyongo et ce qu'il advient de vos données.",
        "d_intro": "Nyongo est développé par Gigayar. Vous pouvez supprimer votre compte et vos données à tout moment.",
        "d_app_h": "Dans l'application",
        "d_app": [
            "Ouvrez Nyongo et connectez-vous.",
            "Allez dans <strong>Profil</strong>.",
            "Appuyez sur <strong>Supprimer mon compte</strong>.",
            "Saisissez votre mot de passe, puis appuyez sur <strong>Supprimer définitivement</strong>.",
        ],
        "d_noapp_h": "Sans l'application",
        "d_noapp": "Si vous ne pouvez plus utiliser l'application, écrivez à "
        "<a href=\"mailto:{support}?subject=Supprimer%20mon%20compte\">{support}</a> depuis l'adresse e-mail de "
        "votre compte, avec pour objet «&nbsp;Supprimer mon compte&nbsp;». Nous vous répondrons pour confirmer "
        "la suppression.",
        "d_gone_h": "Ce qui est supprimé",
        "d_gone": [
            "Votre compte&nbsp;: nom, adresse e-mail, numéro de téléphone et mot de passe.",
            "Vos dettes privées et les contacts que vous avez ajoutés.",
            "Vos messages.",
            "Les demandes que vous avez envoyées et qui n'ont jamais reçu de réponse.",
            "Le jeton de notification de votre téléphone.",
        ],
        "d_kept_h": "Ce qui est conservé",
        "d_kept": "Les dettes que vous avez partagées avec d'autres personnes, et qu'elles ont acceptées, restent dans "
        "leurs registres comme notes privées, car elles font aussi partie de leur historique. Elles gardent votre "
        "nom tel qu'il figurait sur la dette, ne sont plus liées à aucun compte, et aucun rappel n'est envoyé à "
        "leur sujet.",
        "d_more": "Consultez la <a href=\"{privacy}\">Politique de confidentialité</a> pour en savoir plus sur la "
        "façon dont Nyongo traite vos données.",
        # 404
        "nf_title": "Page introuvable",
        "nf_text": "Cette page n'existe pas ou a été déplacée.",
        "nf_home": "Retour à l'accueil",
    },
}


# --------------------------------------------------------------------------- layout

def page_url(lang, path):
    """Public URL of a page; path is '' or like 'nyongo/privacy'."""
    prefix = "fr/" if lang == "fr" else ""
    full = prefix + path
    return f"{DOMAIN}/{full}/" if full else f"{DOMAIN}/"


class Ctx:
    """Builds relative links so the site also works before the custom domain is set up."""

    def __init__(self, lang, path, absolute=False):
        self.lang, self.path = lang, path
        if absolute:
            self.root = "/"
        else:
            depth = len([p for p in path.split("/") if p]) + (1 if lang == "fr" else 0)
            self.root = "../" * depth if depth else "./"

    def link(self, path, lang=None):
        lang = lang or self.lang
        target = ("fr/" if lang == "fr" else "") + path
        return self.root + (target + "/" if target else "")

    def asset(self, name):
        return self.root + "assets/" + name


def layout(ctx, title, desc, body, current=""):
    t = T[ctx.lang]
    other = "fr" if ctx.lang == "en" else "en"
    alternates = "".join(
        f'<link rel="alternate" hreflang="{lg}" href="{page_url(lg, ctx.path)}">' for lg in LANGS
    )
    def nav_link(href, label, key):
        cur = ' aria-current="page"' if key == current else ""
        return f'<a href="{href}"{cur}>{label}</a>'

    return f"""<!doctype html>
<html lang="{ctx.lang}">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>{title}</title>
<meta name="description" content="{html.escape(desc)}">
<link rel="canonical" href="{page_url(ctx.lang, ctx.path)}">
{alternates}<link rel="alternate" hreflang="x-default" href="{page_url("en", ctx.path)}">
<meta property="og:title" content="{title}">
<meta property="og:description" content="{html.escape(desc)}">
<meta property="og:url" content="{page_url(ctx.lang, ctx.path)}">
<meta property="og:type" content="website">
<meta property="og:site_name" content="Gigayar">
<meta name="theme-color" content="#1A1A2E">
<link rel="icon" href="{ctx.root}favicon.svg" type="image/svg+xml">
<link rel="preload" href="{ctx.asset("inter-latin.woff2")}" as="font" type="font/woff2" crossorigin>
<link rel="stylesheet" href="{ctx.asset("style.css")}">
</head>
<body>
<a class="skip" href="#main">{t["skip"]}</a>
<header class="site-header">
  <div class="wrap">
    <a class="brand" href="{ctx.link("")}">gigayar<span>.</span></a>
    <nav class="site-nav" aria-label="Main">
      {nav_link(ctx.link("nyongo"), "Nyongo", "nyongo")}
      {nav_link(ctx.link("") + "#contact", t["nav_contact"], "contact")}
      <a class="lang" href="{ctx.link(ctx.path, other)}" hreflang="{other}" lang="{other}"
         aria-label="{t["lang_switch_label"]}">{t["lang_switch"]}</a>
    </nav>
  </div>
</header>
<main id="main">
{body}
</main>
<footer class="site-footer">
  <div class="wrap">
    <div>© {date.today().year} Gigayar · {t["footer_tag"]}</div>
    <nav aria-label="Footer">
      <a href="{ctx.link("nyongo")}">Nyongo</a>
      <a href="{ctx.link("nyongo/privacy")}">{t["privacy"]}</a>
      <a href="{ctx.link("nyongo/terms")}">{t["terms"]}</a>
      <a href="mailto:{SUPPORT}">{SUPPORT}</a>
    </nav>
  </div>
</footer>
</body>
</html>
"""


# --------------------------------------------------------------------------- pages

def home(ctx):
    t = T[ctx.lang]
    body = f"""
<section class="hero">
  <div class="wrap">
    <h1>{t["home_h1"]}</h1>
    <p class="lead">{t["home_lead"]}</p>
    <div class="actions">
      <a class="btn btn-primary" href="{ctx.link("nyongo")}">{t["home_cta"]}</a>
      <a class="btn btn-secondary" href="mailto:{SUPPORT}">{t["home_cta2"]}</a>
    </div>
  </div>
</section>

<section class="section-soft" id="products">
  <div class="wrap">
    <span class="eyebrow">{t["products_eyebrow"]}</span>
    <h2 class="section-title">{t["products_title"]}</h2>
    <div class="grid-2">
      <a class="product product-nyongo" href="{ctx.link("nyongo")}">
        <span class="tag">{t["nyongo_tag"]}</span>
        <h3>Nyongo</h3>
        <p>{t["nyongo_card"]}</p>
        <span class="more">{t["learn_more"]}</span>
      </a>
      <div class="product product-soon">
        <span class="tag">{t["soon_tag"]}</span>
        <h3>{t["soon_title"]}</h3>
        <p>{t["soon_text"]}</p>
      </div>
    </div>
  </div>
</section>

<section>
  <div class="wrap">
    <span class="eyebrow">{t["principles_eyebrow"]}</span>
    <h2 class="section-title">{t["principles_title"]}</h2>
    <div class="grid-3">
      <div class="card"><div class="icon">{icon("bulb")}</div><h3>{t["p1_t"]}</h3><p>{t["p1"]}</p></div>
      <div class="card"><div class="icon">{icon("eye")}</div><h3>{t["p2_t"]}</h3><p>{t["p2"]}</p></div>
      <div class="card"><div class="icon">{icon("lock")}</div><h3>{t["p3_t"]}</h3><p>{t["p3"]}</p></div>
    </div>
  </div>
</section>

<section class="section-soft contact" id="contact">
  <div class="wrap">
    <h2>{t["contact_title"]}</h2>
    <p>{t["contact_text"]}</p>
    <a class="mail" href="mailto:{SUPPORT}">{SUPPORT}</a>
  </div>
</section>
"""
    return layout(ctx, t["home_title"], t["home_desc"], body)


def nyongo(ctx):
    t = T[ctx.lang]
    subject = t["n_beta_subject"].replace(" ", "%20")
    features = "\n".join(
        f'<div class="card"><div class="icon">{icon(i)}</div><h3>{h}</h3><p>{p}</p></div>' for i, h, p in t["f"]
    )
    steps = "\n".join(f"<li><h3>{h}</h3><p>{p}</p></li>" for h, p in t["s"])
    body = f"""
<section class="n-hero">
  <div class="wrap">
    <span class="by">{t["n_by"]}</span>
    <h1>Nyongo</h1>
    <p class="slogan">{t["n_slogan"]}</p>
    <p class="lead">{t["n_lead"]}</p>
    <span class="pill">{t["n_status"]}</span>
    <div class="actions">
      <a class="btn btn-lime" href="mailto:{SUPPORT}?subject={subject}">{t["n_beta"]}</a>
    </div>
  </div>
</section>

<section>
  <div class="wrap">
    <span class="eyebrow">{t["n_features_eyebrow"]}</span>
    <h2 class="section-title">{t["n_features_title"]}</h2>
    <div class="grid-3">
{features}
    </div>
  </div>
</section>

<section class="section-soft">
  <div class="wrap">
    <span class="eyebrow">{t["n_how_eyebrow"]}</span>
    <h2 class="section-title">{t["n_how_title"]}</h2>
    <ol class="steps">
{steps}
    </ol>
  </div>
</section>

<section>
  <div class="wrap">
    <div class="callout">
      <div class="icon">{icon("wallet", 26)}</div>
      <div><h2>{t["n_money_title"]}</h2><p>{t["n_money"]}</p></div>
    </div>
  </div>
</section>

<section class="section-soft">
  <div class="wrap">
    <h2 class="section-title">{t["n_more_title"]}</h2>
    <div class="link-row">
      <a href="{ctx.link("nyongo/privacy")}">{t["privacy"]}</a>
      <a href="{ctx.link("nyongo/terms")}">{t["terms"]}</a>
      <a href="{ctx.link("nyongo/delete-account")}">{t["delete"]}</a>
      <a href="mailto:{SUPPORT}">{t["support"]} · {SUPPORT}</a>
    </div>
  </div>
</section>
"""
    return layout(ctx, t["n_title"], t["n_desc"], body, current="nyongo")


def crumb(ctx):
    return f'<p class="crumb"><a href="{ctx.link("nyongo")}">← Nyongo</a></p>'


def linkify(text):
    return text.replace(SUPPORT, f'<a href="mailto:{SUPPORT}">{SUPPORT}</a>')


def legal_to_html(text):
    """Same format the app renders: '# ' title, '## ' section, '- ' bullet, the line after the title is meta."""
    out, bullets, title, meta_next = [], [], "", False

    def flush():
        if bullets:
            out.append("<ul>" + "".join(f"<li>{b}</li>" for b in bullets) + "</ul>")
            bullets.clear()

    for raw in text.splitlines():
        line = raw.strip()
        esc = linkify(html.escape(line, quote=False))
        if line.startswith("- "):
            bullets.append(linkify(html.escape(line[2:], quote=False)))
            continue
        flush()
        if not line:
            continue
        if line.startswith("## "):
            out.append(f"<h2>{html.escape(line[3:], quote=False)}</h2>")
        elif line.startswith("# "):
            title = line[2:]
            out.append(f"<h1>{html.escape(title, quote=False)}</h1>")
            meta_next = True
            continue
        elif meta_next:
            out.append(f'<p class="meta">{esc}</p>')
        else:
            out.append(f"<p>{esc}</p>")
        meta_next = False
    flush()
    return title, "\n".join(out)


def legal(ctx, name):
    t = T[ctx.lang]
    text = (LEGAL / f"{name}_{ctx.lang}.txt").read_text(encoding="utf-8")
    title, content = legal_to_html(text)
    body = f'<article class="doc">{crumb(ctx)}\n{content}\n</article>'
    return layout(ctx, f"{title} · Nyongo", t[name] + " · Nyongo", body)


def delete_account(ctx):
    t = T[ctx.lang]
    steps = "".join(f"<li>{s}</li>" for s in t["d_app"])
    gone = "".join(f"<li>{s}</li>" for s in t["d_gone"])
    body = f"""<article class="doc">{crumb(ctx)}
<h1>{t["d_title"]}</h1>
<p class="meta">{t["d_intro"]}</p>
<h2>{t["d_app_h"]}</h2>
<ol>{steps}</ol>
<h2>{t["d_noapp_h"]}</h2>
<p>{t["d_noapp"].format(support=SUPPORT)}</p>
<h2>{t["d_gone_h"]}</h2>
<ul>{gone}</ul>
<h2>{t["d_kept_h"]}</h2>
<p>{t["d_kept"]}</p>
<p class="note">{t["d_more"].format(privacy=ctx.link("nyongo/privacy"))}</p>
</article>"""
    return layout(ctx, t["d_title"], t["d_desc"], body)


def not_found():
    # Served by GitHub Pages at any missing URL, so links must be absolute.
    ctx = Ctx("en", "", absolute=True)
    en, fr = T["en"], T["fr"]
    body = f"""<article class="doc">
<h1>{en["nf_title"]}</h1>
<p class="meta">{en["nf_text"]} <span lang="fr">{fr["nf_text"]}</span></p>
<div class="actions">
  <a class="btn btn-primary" href="/">{en["nf_home"]}</a>
  <a class="btn btn-secondary" href="/fr/" lang="fr">{fr["nf_home"]}</a>
</div>
</article>"""
    page = layout(ctx, en["nf_title"] + " · Gigayar", en["nf_text"], body)
    return re.sub(r'<link rel="(canonical|alternate)"[^>]*>\n?', "", page)


PAGES = {
    "": home,
    "nyongo": nyongo,
    "nyongo/privacy": lambda ctx: legal(ctx, "privacy"),
    "nyongo/terms": lambda ctx: legal(ctx, "terms"),
    "nyongo/delete-account": delete_account,
}

FAVICON = """<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 64 64">
<rect width="64" height="64" rx="14" fill="#1A1A2E"/>
<text x="32" y="44" text-anchor="middle" font-family="Inter, Arial, sans-serif" font-size="40" font-weight="800"
fill="#ffffff">g</text><circle cx="49" cy="40" r="4" fill="#CDFF00"/>
</svg>
"""


def write(rel, content):
    target = OUT / rel
    target.parent.mkdir(parents=True, exist_ok=True)
    target.write_text(content, encoding="utf-8", newline="\n")


def build():
    urls = []
    for lang in LANGS:
        for path, render in PAGES.items():
            prefix = "fr/" if lang == "fr" else ""
            rel = (prefix + path + "/" if prefix + path else "") + "index.html"
            write(rel, render(Ctx(lang, path)))
            urls.append(page_url(lang, path))
    write("404.html", not_found())
    write("favicon.svg", FAVICON)
    write("CNAME", "gigayar.com\n")
    write(".nojekyll", "")
    write("robots.txt", f"User-agent: *\nAllow: /\nSitemap: {DOMAIN}/sitemap.xml\n")
    write(
        "sitemap.xml",
        '<?xml version="1.0" encoding="UTF-8"?>\n<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">\n'
        + "".join(f"  <url><loc>{u}</loc></url>\n" for u in urls)
        + "</urlset>\n",
    )
    print(f"Built {len(urls)} pages + 404 into {OUT}")


def main():
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("--sync-legal", metavar="PATH", help="copy the app's assets/legal/*.txt first")
    args = parser.parse_args()
    if args.sync_legal:
        src = Path(args.sync_legal)
        files = sorted(src.glob("*.txt"))
        if not files:
            raise SystemExit(f"No .txt files in {src}")
        for f in files:
            shutil.copy2(f, LEGAL / f.name)
        print(f"Copied {len(files)} legal texts from {src}")
    build()


if __name__ == "__main__":
    main()
