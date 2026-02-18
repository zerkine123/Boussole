'use client';

import { useTranslations } from 'next-intl';
import { useState } from 'react';
import { useRouter } from 'next/navigation';
import { Card, CardContent, CardHeader, CardFooter } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { Checkbox } from '@/components/ui/checkbox';
import { Label } from '@/components/ui/label';
import { RadioGroup, RadioGroupItem } from '@/components/ui/radio-group';
import { Input } from '@/components/ui/input';
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from '@/components/ui/select';
import { ChevronRight, ChevronLeft, CheckCircle2, Loader2, Briefcase, Layers, Map, Globe } from 'lucide-react';
import DashboardLayout from "@/components/DashboardLayout";
import { Progress } from "@/components/ui/progress";

type OnboardingStep = {
  id: number;
  title: string;
  description: string;
  icon: React.ReactNode;
};

export default function OnboardingPage() {
  const t = useTranslations('onboarding');
  const router = useRouter();

  const steps: OnboardingStep[] = [
    {
      id: 1,
      title: t('steps.useCase.title'),
      description: t('steps.useCase.description'),
      icon: <Briefcase className="h-5 w-5" />,
    },
    {
      id: 2,
      title: t('steps.sectors.title'),
      description: t('steps.sectors.description'),
      icon: <Layers className="h-5 w-5" />,
    },
    {
      id: 3,
      title: t('steps.wilayas.title'),
      description: t('steps.wilayas.description'),
      icon: <Map className="h-5 w-5" />,
    },
    {
      id: 4,
      title: t('steps.language.title'),
      description: t('steps.language.description'),
      icon: <Globe className="h-5 w-5" />,
    },
    {
      id: 5,
      title: t('steps.organization.title'),
      description: t('steps.organization.description'),
      icon: <Briefcase className="h-5 w-5" />,
    }
  ];

  const [currentStep, setCurrentStep] = useState(1);
  const [useCase, setUseCase] = useState<string>('');
  const [selectedSectors, setSelectedSectors] = useState<number[]>([]);
  const [selectedWilayas, setSelectedWilayas] = useState<number[]>([]);
  const [preferredLanguage, setPreferredLanguage] = useState('en');
  const [organization, setOrganization] = useState('');
  const [isLoading, setIsLoading] = useState(false);
  const [isCompleted, setIsCompleted] = useState(false);
  const [error, setError] = useState('');

  const sectors = [
    { id: 1, name: t('sectors.agriculture'), icon: 'leaf' },
    { id: 2, name: t('sectors.energy'), icon: 'zap' },
    { id: 3, name: t('sectors.manufacturing'), icon: 'factory' },
    { id: 4, name: t('sectors.services'), icon: 'briefcase' },
    { id: 5, name: t('sectors.tourism'), icon: 'plane' },
  ];

  const wilayas = [
    { id: 1, name: 'Algiers', code: '01' },
    { id: 2, name: 'Oran', code: '31' },
    { id: 3, name: 'Constantine', code: '25' },
    { id: 4, name: 'Setif', code: '16' },
    { id: 5, name: 'Batna', code: '07' },
    { id: 6, name: 'Annaba', code: '19' },
    { id: 7, name: 'Skikda', code: '47' },
    { id: 8, name: 'Tlemcen', code: '22' },
    { id: 9, name: 'Tizi Ouzou', code: '23' },
    { id: 10, name: 'Béjaïa', code: '08' },
    { id: 11, name: 'Biskra', code: '25' },
    { id: 12, name: 'Boumerdès', code: '35' },
    { id: 13, name: 'Tébessa', code: '12' },
    { id: 14, name: 'Jijel', code: '21' },
    { id: 15, name: 'Sétif', code: '29' },
    { id: 16, name: 'Tamanrasset', code: '22' },
    { id: 17, name: 'El Oued', code: '39' },
    { id: 18, name: 'Ghardaïa', code: '24' },
    { id: 19, name: 'Khenchela', code: '13' },
    { id: 20, name: 'Souk Ahras', code: '19' },
    { id: 21, name: 'Tipaza', code: '37' },
    { id: 22, name: 'Mila', code: '43' },
    { id: 23, name: 'Adrar', code: '06' },
    { id: 24, name: 'El Tarf', code: '17' },
    { id: 25, name: 'Tindouf', code: '11' },
    { id: 26, name: 'Ghardaïa', code: '47' },
    { id: 27, name: "El M'Ghaïr", code: '40' },
    { id: 28, name: 'Naâma', code: '31' },
    { id: 29, name: 'Tamanrasset', code: '02' },
    { id: 30, name: 'Ouargla', code: '31' },
    { id: 31, name: 'Tébessa', code: '12' },
    { id: 32, name: 'Illizi', code: '35' },
    { id: 33, name: 'Bordj Bou Arreridj', code: '10' },
    { id: 34, name: 'Béjaïa', code: '08' },
    { id: 35, name: 'Biskra', code: '25' },
    { id: 36, name: "M'Sila", code: '26' },
    { id: 37, name: 'Tébessa', code: '12' },
    { id: 38, name: 'Souk Ahras', code: '19' },
    { id: 39, name: 'El Bayadh', code: '17' },
    { id: 40, name: 'Tindouf', code: '11' },
    { id: 41, name: 'Tlemcen', code: '22' },
    { id: 42, name: 'El Oued', code: '39' },
    { id: 43, name: 'Khenchela', code: '13' },
    { id: 44, name: 'Tipaza', code: '37' },
    { id: 45, name: 'Laghouat', code: '26' },
    { id: 46, name: 'Guelma', code: '47' },
    { id: 47, name: 'Relizane', code: '48' },
    { id: 48, name: 'Tébessa', code: '12' },
  ];

  const handleNext = async () => {
    // If not last step, iterate to next step
    if (currentStep < 5) {
      setCurrentStep(prev => prev + 1);
      return;
    }

    // Last step: Submit
    setIsLoading(true);
    setError('');

    try {
      // API call to save preferences
      const response = await fetch('/api/v1/onboarding/complete', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          'Authorization': `Bearer ${localStorage.getItem('access_token')}`,
        },
        body: JSON.stringify({
          preferences: {
            use_case: useCase,
            sectors_of_interest: selectedSectors,
            wilayas_of_interest: selectedWilayas,
            preferred_language: preferredLanguage,
            organization: organization,
          },
        }),
      });

      if (!response.ok) {
        throw new Error('Failed to save preferences');
      }

      const data = await response.json();
      setIsCompleted(true);
      router.push('/dashboard');
    } catch (err) {
      setError(err instanceof Error ? err.message : 'An error occurred');
    } finally {
      setIsLoading(false);
    }
  };

  const handleBack = () => {
    if (currentStep > 1) {
      setCurrentStep(prev => prev - 1);
    }
  };

  const handleSkip = async () => {
    setIsLoading(true);

    try {
      const response = await fetch('/api/v1/onboarding/skip', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          'Authorization': `Bearer ${localStorage.getItem('access_token')}`,
        },
        body: JSON.stringify({}),
      });

      if (!response.ok) {
        throw new Error('Failed to skip onboarding');
      }

      router.push('/dashboard');
    } catch (err) {
      setError(err instanceof Error ? err.message : 'An error occurred');
    } finally {
      setIsLoading(false);
    }
  };

  const toggleSector = (sectorId: number) => {
    setSelectedSectors((prev) =>
      prev.includes(sectorId)
        ? prev.filter((id) => id !== sectorId)
        : [...prev, sectorId]
    );
  };

  const toggleWilaya = (wilayaId: number) => {
    setSelectedWilayas((prev) =>
      prev.includes(wilayaId)
        ? prev.filter((id) => id !== wilayaId)
        : [...prev, wilayaId]
    );
  };

  const progressPercentage = (currentStep / 5) * 100;

  return (
    <DashboardLayout>
      <div className="container mx-auto px-4 py-8">
        <div className="max-w-2xl mx-auto">
          {/* Header and Progress */}
          <div className="mb-8 text-center">
            <h1 className="text-3xl font-bold mb-2 text-foreground">{t('title')}</h1>
            <p className="text-muted-foreground mb-6">{t('subtitle')}</p>
            <div className="space-y-2">
              <div className="flex justify-between text-sm text-muted-foreground">
                <span>{t('buttons.step', { current: currentStep, total: 5, defaultMessage: `Step ${currentStep} of 5` })}</span>
                <span>{Math.round(progressPercentage)}%</span>
              </div>
              <Progress value={progressPercentage} className="h-2" />
            </div>
          </div>

          {/* Step Content */}
          <div className="min-h-[400px]">
            {/* Step 1: Use Case */}
            {currentStep === 1 && (
              <Card className="animate-in fade-in slide-in-from-right-4 duration-300">
                <CardHeader>
                  <h2 className="text-xl font-semibold">{t('steps.useCase.title')}</h2>
                  <p className="text-muted-foreground">{t('steps.useCase.description')}</p>
                </CardHeader>
                <CardContent>
                  <RadioGroup value={useCase} onValueChange={setUseCase} className="grid grid-cols-1 gap-4">
                    {['personal', 'business', 'academic', 'government'].map((val) => (
                      <div key={val} className={`flex items-center space-x-3 border rounded-lg p-4 cursor-pointer transition-colors ${useCase === val ? 'border-primary bg-primary/5' : 'hover:bg-muted/50'}`}>
                        <RadioGroupItem value={val} id={val} />
                        <Label htmlFor={val} className="cursor-pointer font-medium capitalize flex-1">{t(`steps.useCase.options.${val}`)}</Label>
                      </div>
                    ))}
                  </RadioGroup>
                </CardContent>
              </Card>
            )}

            {/* Step 2: Sectors */}
            {currentStep === 2 && (
              <Card className="animate-in fade-in slide-in-from-right-4 duration-300">
                <CardHeader>
                  <h2 className="text-xl font-semibold">{t('steps.sectors.title')}</h2>
                  <p className="text-muted-foreground">{t('steps.sectors.description')}</p>
                </CardHeader>
                <CardContent>
                  <div className="grid grid-cols-1 sm:grid-cols-2 gap-4">
                    {sectors.map((sector) => (
                      <div
                        key={sector.id}
                        className={`
                                    p-4 border rounded-xl cursor-pointer transition-all duration-200
                                    ${selectedSectors.includes(sector.id)
                            ? 'border-primary bg-primary/5 ring-1 ring-primary/20'
                            : 'border-border hover:border-primary/50 hover:bg-muted/50'}
                                    `}
                        onClick={() => toggleSector(sector.id)}
                      >
                        <div className="flex items-start gap-3">
                          <Checkbox
                            checked={selectedSectors.includes(sector.id)}
                            onCheckedChange={() => toggleSector(sector.id)}
                            className="mt-1"
                          />
                          <div>
                            <div className="font-medium text-foreground">{sector.name}</div>
                          </div>
                        </div>
                      </div>
                    ))}
                  </div>
                </CardContent>
              </Card>
            )}

            {/* Step 3: Wilayas */}
            {currentStep === 3 && (
              <Card className="animate-in fade-in slide-in-from-right-4 duration-300">
                <CardHeader>
                  <h2 className="text-xl font-semibold">{t('steps.wilayas.title')}</h2>
                  <p className="text-muted-foreground">{t('steps.wilayas.description')}</p>
                </CardHeader>
                <CardContent>
                  <div className="grid grid-cols-2 sm:grid-cols-3 gap-3 max-h-[400px] overflow-y-auto pr-2">
                    {wilayas.map((wilaya) => (
                      <div
                        key={wilaya.id}
                        className={`
                                    p-3 border rounded-lg cursor-pointer transition-all
                                    ${selectedWilayas.includes(wilaya.id)
                            ? 'border-primary bg-primary/5'
                            : 'border-border hover:border-primary/50'}
                                    `}
                        onClick={() => toggleWilaya(wilaya.id)}
                      >
                        <div className="flex items-center gap-2">
                          <Checkbox
                            checked={selectedWilayas.includes(wilaya.id)}
                            onCheckedChange={() => toggleWilaya(wilaya.id)}
                          />
                          <div className="flex-1 min-w-0">
                            <div className="font-medium truncate text-sm">{wilaya.name}</div>
                            <div className="text-xs text-muted-foreground">{wilaya.code}</div>
                          </div>
                        </div>
                      </div>
                    ))}
                  </div>
                </CardContent>
              </Card>
            )}

            {/* Step 4: Language */}
            {currentStep === 4 && (
              <Card className="animate-in fade-in slide-in-from-right-4 duration-300">
                <CardHeader>
                  <h2 className="text-xl font-semibold">{t('steps.language.title')}</h2>
                  <p className="text-muted-foreground">{t('steps.language.description')}</p>
                </CardHeader>
                <CardContent>
                  <Select value={preferredLanguage} onValueChange={setPreferredLanguage}>
                    <SelectTrigger className="w-full h-12">
                      <SelectValue placeholder={t('steps.language.description')} />
                    </SelectTrigger>
                    <SelectContent>
                      <SelectItem value="en">English</SelectItem>
                      <SelectItem value="fr">Français</SelectItem>
                      <SelectItem value="ar">العربية</SelectItem>
                    </SelectContent>
                  </Select>
                </CardContent>
              </Card>
            )}

            {/* Step 5: Organization */}
            {currentStep === 5 && (
              <Card className="animate-in fade-in slide-in-from-right-4 duration-300">
                <CardHeader>
                  <h2 className="text-xl font-semibold">{t('steps.organization.title')}</h2>
                  <p className="text-muted-foreground">{t('steps.organization.description')}</p>
                </CardHeader>
                <CardContent>
                  <div className="space-y-2">
                    <Label htmlFor="organization" className="text-base">{t('steps.organization.title')}</Label>
                    <Input
                      id="organization"
                      type="text"
                      placeholder={t('steps.organization.placeholder')}
                      value={organization}
                      onChange={(e) => setOrganization(e.target.value)}
                      className="w-full h-11"
                    />
                  </div>
                </CardContent>
              </Card>
            )}
          </div>

          {/* Error Display */}
          {error && (
            <div className="mt-6 p-4 bg-destructive/10 border border-destructive/20 rounded-lg flex items-center gap-3">
              <div className="h-2 w-2 rounded-full bg-destructive" />
              <p className="text-destructive font-medium text-sm">{error}</p>
            </div>
          )}

          {/* Controls */}
          <div className="mt-8 flex justify-between items-center bg-background/50 backdrop-blur-sm p-4 rounded-xl border">
            <Button variant="ghost" onClick={handleBack} disabled={currentStep === 1}>
              <ChevronLeft className="mr-2 h-4 w-4" /> {t('buttons.previous')}
            </Button>

            <div className="flex gap-4 items-center">
              <Button variant="ghost" onClick={handleSkip} className="text-muted-foreground">
                {t('buttons.skip')}
              </Button>
              <Button onClick={handleNext} disabled={isLoading} className="min-w-[120px]">
                {isLoading ? (
                  <Loader2 className="animate-spin h-4 w-4" />
                ) : currentStep === 5 ? (
                  t('buttons.submit')
                ) : (
                  <>
                    {t('buttons.next')} <ChevronRight className="ml-2 h-4 w-4" />
                  </>
                )}
              </Button>
            </div>
          </div>

          {/* Success Overlay */}
          {isCompleted && (
            <div className="fixed inset-0 flex items-center justify-center bg-black/60 backdrop-blur-sm z-[100] animate-in fade-in duration-300">
              <Card className="max-w-md w-full mx-4 shadow-2xl border-none">
                <CardContent className="pt-8 pb-8">
                  <div className="text-center">
                    <div className="mb-6">
                      <div className="h-20 w-20 bg-green-100 dark:bg-green-900/30 rounded-full flex items-center justify-center mx-auto animate-bounce-slow">
                        <CheckCircle2 className="h-10 w-10 text-green-600 dark:text-green-400" />
                      </div>
                    </div>
                    <h2 className="text-2xl font-bold mb-3 text-foreground">{t('success.title')}</h2>
                    <p className="text-muted-foreground mb-8 px-4 leading-relaxed">{t('success.message')}</p>
                    <Button onClick={() => router.push(`/${preferredLanguage}/dashboard`)} className="w-full h-11 text-base font-medium">
                      {t('success.button')} <ChevronRight className="ml-2 h-4 w-4" />
                    </Button>
                  </div>
                </CardContent>
              </Card>
            </div>
          )}

        </div>
      </div>
    </DashboardLayout>
  );
}
