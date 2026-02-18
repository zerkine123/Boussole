"use client";

import { useTranslations } from "next-intl";
import Link from "next/link";
import {
  Compass,
  ArrowRight,
  BarChart3,
  Database,
  Globe,
  Check,
  Mail,
  Phone,
  MapPin,
  Menu,
  X,
  Facebook,
  Twitter,
  Linkedin,
  Instagram,
  ChevronRight
} from "lucide-react";
import { useState } from "react";
import { Button } from "@/components/ui/button";

export default function HomePage() {
  const t = useTranslations();
  const [mobileMenuOpen, setMobileMenuOpen] = useState(false);

  const toggleMenu = () => setMobileMenuOpen(!mobileMenuOpen);

  return (
    <div className="min-h-screen bg-background text-foreground overflow-x-hidden selection:bg-primary/20 selection:text-primary">

      {/* Navigation */}
      <header className="fixed top-0 left-0 right-0 z-50 bg-background/80 backdrop-blur-md border-b border-border transition-all duration-300">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="flex items-center justify-between h-20">
            {/* Logo */}
            <div className="flex items-center gap-3">
              <div className="h-10 w-10 rounded-xl bg-primary/10 flex items-center justify-center border border-primary/20 shadow-sm">
                <Compass className="h-6 w-6 text-primary" />
              </div>
              <span className="text-xl font-bold tracking-tight text-foreground">
                {t("common.appName")}
              </span>
            </div>

            {/* Desktop Nav */}
            <nav className="hidden md:flex items-center gap-8">
              <NavLink href="#about">{t("about.title")}</NavLink>
              <NavLink href="#features">{t("sectors.title")}</NavLink>
              <NavLink href="#pricing">{t("pricing.title")}</NavLink>
              <NavLink href="#contact">{t("contact.title")}</NavLink>
            </nav>

            {/* Auth Buttons */}
            <div className="hidden md:flex items-center gap-4">
              <Link href="/login" className="text-sm font-medium text-muted-foreground hover:text-primary transition-colors">
                {t("nav.login")}
              </Link>
              <Link href="/register">
                <Button className="rounded-full px-6 shadow-lg shadow-primary/20">
                  {t("nav.register")}
                </Button>
              </Link>
            </div>

            {/* Mobile Menu Toggle */}
            <button className="md:hidden p-2 text-muted-foreground" onClick={toggleMenu}>
              {mobileMenuOpen ? <X className="h-6 w-6" /> : <Menu className="h-6 w-6" />}
            </button>
          </div>
        </div>

        {/* Mobile Menu */}
        {mobileMenuOpen && (
          <div className="md:hidden bg-background border-b border-border p-4 space-y-4 animate-fade-in-up">
            <MobileNavLink href="#about" onClick={toggleMenu}>{t("about.title")}</MobileNavLink>
            <MobileNavLink href="#features" onClick={toggleMenu}>{t("sectors.title")}</MobileNavLink>
            <MobileNavLink href="#pricing" onClick={toggleMenu}>{t("pricing.title")}</MobileNavLink>
            <MobileNavLink href="#contact" onClick={toggleMenu}>{t("contact.title")}</MobileNavLink>
            <hr className="border-border" />
            <div className="flex flex-col gap-3">
              <Link href="/login" className="w-full">
                <Button variant="ghost" className="w-full justify-start">{t("nav.login")}</Button>
              </Link>
              <Link href="/register" className="w-full">
                <Button className="w-full">{t("nav.register")}</Button>
              </Link>
            </div>
          </div>
        )}
      </header>

      {/* Hero Section */}
      <section className="relative pt-32 pb-20 lg:pt-48 lg:pb-32 overflow-hidden">
        <div className="absolute inset-0 -z-10">
          <div className="absolute top-[20%] left-[10%] w-72 h-72 bg-primary/10 rounded-full blur-3xl opacity-50 animate-pulse" />
          <div className="absolute bottom-[20%] right-[10%] w-96 h-96 bg-accent/20 rounded-full blur-3xl opacity-50" />
        </div>

        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 text-center">
          <span className="inline-block py-1 px-3 rounded-full bg-primary/10 text-primary text-sm font-medium mb-6 animate-fade-in">
            🚀 powered by AI & Real-time Data
          </span>
          <h1 className="text-5xl md:text-6xl lg:text-7xl font-bold bg-clip-text text-transparent bg-gradient-to-r from-primary to-emerald-700 mb-6 tracking-tight leading-tight max-w-4xl mx-auto">
            {t("common.welcome")}
          </h1>
          <p className="text-xl text-muted-foreground max-w-2xl mx-auto mb-10 leading-relaxed">
            {t("about.missionText")}
          </p>
          <div className="flex flex-col sm:flex-row items-center justify-center gap-4">
            <Link href="/dashboard">
              <Button size="lg" className="rounded-full px-8 text-lg h-14 shadow-xl shadow-primary/20 hover:shadow-2xl hover:shadow-primary/30 transition-all">
                {t("nav.dashboard")} <ArrowRight className="ml-2 h-5 w-5" />
              </Button>
            </Link>
            <Link href="/data">
              <Button size="lg" variant="outline" className="rounded-full px-8 text-lg h-14 border-2 bg-background/50 backdrop-blur-sm">
                {t("nav.data")}
              </Button>
            </Link>
          </div>
        </div>
      </section>

      {/* Stats Band */}
      <section className="py-12 bg-primary/5 border-y border-primary/10">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="grid grid-cols-2 md:grid-cols-4 gap-8">
            <StatItem value="2.4M+" label="Registered Entities" />
            <StatItem value="8,000+" label="Startups" />
            <StatItem value="192" label="Incubators" />
            <StatItem value="99.9%" label="Uptime" />
          </div>
        </div>
      </section>

      {/* About Us */}
      <section id="about" className="py-24 relative">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="text-center mb-16">
            <h2 className="text-3xl font-bold text-foreground mb-4">{t("about.title")}</h2>
            <p className="text-muted-foreground max-w-2xl mx-auto">{t("about.missionText")}</p>
          </div>

          <div className="grid grid-cols-1 md:grid-cols-3 gap-8">
            <FeatureCard
              icon={<Globe className="h-8 w-8 text-primary" />}
              title={t("about.value1")}
              description={t("about.value1Text")}
            />
            <FeatureCard
              icon={<Compass className="h-8 w-8 text-indigo-500" />}
              title={t("about.value2")}
              description={t("about.value2Text")}
            />
            <FeatureCard
              icon={<BarChart3 className="h-8 w-8 text-amber-500" />}
              title={t("about.value3")}
              description={t("about.value3Text")}
            />
          </div>
        </div>
      </section>

      {/* Sectors / Features */}
      <section id="features" className="py-24 bg-card border-y border-border/50">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="flex flex-col md:flex-row md:items-end justify-between mb-12 gap-6">
            <div>
              <h2 className="text-3xl font-bold text-foreground mb-2">{t("sectors.title")}</h2>
              <p className="text-muted-foreground">{t("sectors.description")}</p>
            </div>
            <Link href="/data" className="text-primary font-medium hover:underline flex items-center">
              View all sectors <ChevronRight className="h-4 w-4" />
            </Link>
          </div>

          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
            {[
              { id: "agriculture", icon: "🌾", color: "text-emerald-600 bg-emerald-50" },
              { id: "energy", icon: "⚡", color: "text-amber-600 bg-amber-50" },
              { id: "manufacturing", icon: "🏭", color: "text-blue-600 bg-blue-50" },
              { id: "services", icon: "💼", color: "text-purple-600 bg-purple-50" },
              { id: "tourism", icon: "✈️", color: "text-indigo-600 bg-indigo-50" },
              { id: "construction", icon: "🏗️", color: "text-orange-600 bg-orange-50" },
            ].map((sector) => (
              <div key={sector.id} className="group p-6 rounded-2xl border border-border bg-background hover:shadow-lg transition-all duration-300 hover:-translate-y-1 cursor-pointer">
                <div className={`h-12 w-12 rounded-xl ${sector.color} flex items-center justify-center text-2xl mb-4 group-hover:scale-110 transition-transform`}>
                  {sector.icon}
                </div>
                <h3 className="text-lg font-semibold text-foreground mb-2">{t(`sectors.${sector.id}.title`)}</h3>
                <p className="text-sm text-muted-foreground">{t(`sectors.${sector.id}.description`)}</p>
              </div>
            ))}
          </div>
        </div>
      </section>

      {/* Pricing */}
      <section id="pricing" className="py-24 relative overflow-hidden">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 relative z-10">
          <div className="text-center mb-16">
            <h2 className="text-3xl font-bold text-foreground mb-4">{t("pricing.title")}</h2>
            <p className="text-muted-foreground">{t("pricing.subtitle")}</p>
          </div>

          <div className="grid grid-cols-1 md:grid-cols-3 gap-8">
            {/* Free Plan */}
            <PricingCard
              title={t("pricing.free.title")}
              price={t("pricing.free.price")}
              period={t("pricing.monthly")}
              description={t("pricing.free.description")}
              features={[
                t("pricing.free.features.1"),
                t("pricing.free.features.2"),
                t("pricing.free.features.3")
              ]}
              buttonText={t("pricing.free.button")}
              variant="outline"
            />
            {/* Pro Plan */}
            <PricingCard
              title={t("pricing.pro.title")}
              price={t("pricing.pro.price")}
              period={t("pricing.monthly")}
              description={t("pricing.pro.description")}
              features={[
                t("pricing.pro.features.1"),
                t("pricing.pro.features.2"),
                t("pricing.pro.features.3"),
                t("pricing.pro.features.4")
              ]}
              buttonText={t("pricing.pro.button")}
              popular
              variant="default"
            />
            {/* Enterprise Plan */}
            <PricingCard
              title={t("pricing.enterprise.title")}
              price={t("pricing.enterprise.price")}
              period={t("pricing.enterprise.period")}
              description={t("pricing.enterprise.description")}
              features={[
                t("pricing.enterprise.features.1"),
                t("pricing.enterprise.features.2"),
                t("pricing.enterprise.features.3"),
                t("pricing.enterprise.features.4"),
                t("pricing.enterprise.features.5")
              ]}
              buttonText={t("pricing.enterprise.button")}
              variant="outline"
            />
          </div>
        </div>
      </section>

      {/* Contact */}
      <section id="contact" className="py-24 bg-primary/5">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="grid grid-cols-1 lg:grid-cols-2 gap-16 items-center">
            <div>
              <h2 className="text-3xl font-bold text-foreground mb-6">{t("contact.title")}</h2>
              <p className="text-muted-foreground mb-8 text-lg">{t("contact.subtitle")}</p>

              <div className="space-y-6">
                <ContactItem icon={<Mail className="h-5 w-5" />} label={t("contact.info.email")} value="hello@boussole.dz" />
                <ContactItem icon={<Phone className="h-5 w-5" />} label={t("contact.info.phone")} value="+213 555 123 456" />
                <ContactItem icon={<MapPin className="h-5 w-5" />} label={t("contact.info.address")} value={t("contact.info.addressText")} />
              </div>

              <div className="flex gap-4 mt-10">
                <SocialLink icon={<Linkedin className="h-5 w-5" />} href="#" />
                <SocialLink icon={<Twitter className="h-5 w-5" />} href="#" />
                <SocialLink icon={<Facebook className="h-5 w-5" />} href="#" />
                <SocialLink icon={<Instagram className="h-5 w-5" />} href="#" />
              </div>
            </div>

            <div className="bg-background rounded-2xl p-8 shadow-xl border border-border">
              <form className="space-y-4">
                <div className="grid grid-cols-2 gap-4">
                  <div className="space-y-2">
                    <label className="text-sm font-medium">{t("contact.form.name")}</label>
                    <input type="text" className="w-full px-4 py-2 rounded-lg border border-input bg-background focus:ring-2 focus:ring-primary focus:border-transparent outline-none transition-all" />
                  </div>
                  <div className="space-y-2">
                    <label className="text-sm font-medium">{t("contact.form.email")}</label>
                    <input type="email" className="w-full px-4 py-2 rounded-lg border border-input bg-background focus:ring-2 focus:ring-primary focus:border-transparent outline-none transition-all" />
                  </div>
                </div>
                <div className="space-y-2">
                  <label className="text-sm font-medium">{t("contact.form.message")}</label>
                  <textarea rows={4} className="w-full px-4 py-2 rounded-lg border border-input bg-background focus:ring-2 focus:ring-primary focus:border-transparent outline-none transition-all resize-none" />
                </div>
                <Button className="w-full h-12 text-base">{t("contact.form.submit")}</Button>
              </form>
            </div>
          </div>
        </div>
      </section>

      {/* Footer */}
      <footer className="bg-foreground text-background py-16 border-t border-white/10">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="grid grid-cols-2 md:grid-cols-4 gap-8 mb-12">
            <div className="col-span-2 md:col-span-1">
              <div className="flex items-center gap-2 mb-6">
                <Compass className="h-6 w-6 text-primary" />
                <span className="text-xl font-bold">{t("common.appName")}</span>
              </div>
              <p className="text-sm text-gray-400 leading-relaxed">
                Empowering Algeria with data-driven insights. Built for growth, designed for clarity.
              </p>
            </div>

            <div>
              <h4 className="font-semibold mb-4 text-white">{t("footer.company")}</h4>
              <ul className="space-y-2 text-sm text-gray-400">
                <li><Link href="#about" className="hover:text-primary transition-colors">{t("footer.about")}</Link></li>
                <li><Link href="#" className="hover:text-primary transition-colors">{t("footer.careers")}</Link></li>
                <li><Link href="#contact" className="hover:text-primary transition-colors">{t("contact.title")}</Link></li>
              </ul>
            </div>

            <div>
              <h4 className="font-semibold mb-4 text-white">{t("footer.legal")}</h4>
              <ul className="space-y-2 text-sm text-gray-400">
                <li><Link href="#" className="hover:text-primary transition-colors">{t("footer.privacy")}</Link></li>
                <li><Link href="#" className="hover:text-primary transition-colors">{t("footer.terms")}</Link></li>
              </ul>
            </div>

            <div>
              <h4 className="font-semibold mb-4 text-white">{t("footer.social")}</h4>
              <ul className="space-y-2 text-sm text-gray-400">
                <li><Link href="#" className="hover:text-primary transition-colors">LinkedIn</Link></li>
                <li><Link href="#" className="hover:text-primary transition-colors">Twitter</Link></li>
                <li><Link href="#" className="hover:text-primary transition-colors">Facebook</Link></li>
              </ul>
            </div>
          </div>

          <div className="border-t border-white/10 pt-8 text-center text-sm text-gray-500">
            {t("footer.rights")}
          </div>
        </div>
      </footer>
    </div>
  );
}

// Components

function NavLink({ href, children }: { href: string; children: React.ReactNode }) {
  return (
    <Link href={href} className="text-sm font-medium text-muted-foreground hover:text-primary transition-colors">
      {children}
    </Link>
  );
}

function MobileNavLink({ href, onClick, children }: { href: string; onClick: () => void; children: React.ReactNode }) {
  return (
    <Link href={href} onClick={onClick} className="block text-base font-medium text-foreground p-2 hover:bg-muted rounded-lg transition-colors">
      {children}
    </Link>
  );
}

function StatItem({ value, label }: { value: string; label: string }) {
  return (
    <div className="text-center p-6 rounded-2xl bg-background border border-border/50 hover:border-primary/30 transition-colors">
      <div className="text-3xl md:text-4xl font-bold text-primary mb-2">{value}</div>
      <div className="text-sm font-medium text-muted-foreground uppercase tracking-wide">{label}</div>
    </div>
  );
}

function FeatureCard({ icon, title, description }: { icon: React.ReactNode; title: string; description: string }) {
  return (
    <div className="bg-background rounded-2xl p-8 border border-border shadow-sm hover:shadow-md transition-all text-center group hover:-translate-y-1">
      <div className="inline-flex h-16 w-16 items-center justify-center rounded-2xl bg-muted mb-6 group-hover:scale-110 transition-transform duration-300">
        {icon}
      </div>
      <h3 className="text-xl font-bold text-foreground mb-3">{title}</h3>
      <p className="text-muted-foreground leading-relaxed">
        {description}
      </p>
    </div>
  );
}

function PricingCard({
  title,
  price,
  period,
  description,
  features,
  buttonText,
  popular = false,
  variant = "outline"
}: any) {
  return (
    <div className={`relative rounded-3xl p-8 ${popular ? 'bg-background border-2 border-primary shadow-2xl scale-105 z-10' : 'bg-background/50 border border-border shadow-sm'}`}>
      {popular && (
        <div className="absolute top-0 left-1/2 -translate-x-1/2 -translate-y-1/2 bg-primary text-primary-foreground text-xs font-bold px-3 py-1 rounded-full uppercase tracking-wider">
          Most Popular
        </div>
      )}
      <div className="mb-6">
        <h3 className="text-lg font-semibold text-muted-foreground mb-2">{title}</h3>
        <div className="flex items-baseline gap-1">
          <span className="text-4xl font-bold text-foreground">{price}</span>
          <span className="text-sm text-muted-foreground">{period}</span>
        </div>
        <p className="text-sm text-muted-foreground mt-4">{description}</p>
      </div>
      <ul className="space-y-4 mb-8">
        {features.map((feature: string, i: number) => (
          <li key={i} className="flex items-center gap-3 text-sm">
            <Check className="h-5 w-5 text-primary shrink-0" />
            <span>{feature}</span>
          </li>
        ))}
      </ul>
      <Button className="w-full" variant={variant}>{buttonText}</Button>
    </div>
  );
}

function ContactItem({ icon, label, value }: { icon: React.ReactNode; label: string; value: string }) {
  return (
    <div className="flex items-center gap-4">
      <div className="h-10 w-10 rounded-full bg-primary/10 flex items-center justify-center text-primary">
        {icon}
      </div>
      <div>
        <div className="text-sm text-muted-foreground">{label}</div>
        <div className="font-medium text-foreground">{value}</div>
      </div>
    </div>
  );
}

function SocialLink({ icon, href }: { icon: React.ReactNode; href: string }) {
  return (
    <a href={href} className="h-10 w-10 rounded-full bg-background border border-border flex items-center justify-center text-muted-foreground hover:bg-primary hover:text-primary-foreground hover:border-primary transition-all duration-300">
      {icon}
    </a>
  );
}
