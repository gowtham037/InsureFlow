import React, { useEffect, useState } from 'react';
import { Header } from '../components/Header';
import { apiClient } from '../api/client';
import { Product } from '../types';
import { Shield, ShieldCheck, Car, Home, Heart, Check, Layers, AlertCircle, Activity } from 'lucide-react';

export const ProductsPage: React.FC = () => {
  const [products, setProducts] = useState<Product[]>([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    const fetchProducts = async () => {
      try {
        const data = await apiClient.getProducts();
        setProducts(data);
      } catch (err) {
        console.error('Failed to fetch products:', err);
      } finally {
        setLoading(false);
      }
    };
    fetchProducts();
  }, []);

  const getProductIcon = (lob: string) => {
    if (lob === 'MOTOR') return <Car className="w-6 h-6 text-blue-600" />;
    if (lob === 'HOME') return <Home className="w-6 h-6 text-emerald-600" />;
    return <Heart className="w-6 h-6 text-rose-600" />;
  };

  return (
    <div className="flex-1 flex flex-col pb-12">
      <Header
        title="Insurance Product Catalog"
        subtitle="Master line-of-business underwriting specifications, coverage riders and actuarial factor ceilings"
      />

      <div className="p-8 space-y-8">
        {loading ? (
          <div className="flex items-center justify-center p-12">
            <Activity className="w-6 h-6 text-brand-600 animate-spin mr-2" />
            <span className="text-sm font-medium text-slate-500">Loading product definitions...</span>
          </div>
        ) : (
          <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
            {products.map((prod) => (
              <div
                key={prod.id}
                className="bg-white rounded-xl border border-slate-200/90 shadow-xs flex flex-col justify-between overflow-hidden hover:border-brand-500/50 hover:shadow-md transition-all duration-200"
              >
                {/* Header */}
                <div className="p-6 border-b border-slate-100 bg-gradient-to-b from-slate-50/50 to-transparent">
                  <div className="flex items-center justify-between mb-4">
                    <div className="w-12 h-12 rounded-xl bg-white border border-slate-200 shadow-xs flex items-center justify-center">
                      {getProductIcon(prod.line_of_business)}
                    </div>
                    <span className="px-2.5 py-1 bg-brand-50 border border-brand-200 text-brand-700 text-xs font-bold rounded-full">
                      {prod.product_code}
                    </span>
                  </div>

                  <h3 className="text-base font-bold text-slate-900 leading-tight mb-1">{prod.name}</h3>
                  <p className="text-xs text-slate-500 leading-relaxed">{prod.description}</p>
                </div>

                {/* Key Underwriting Specs */}
                <div className="p-6 space-y-4 flex-1">
                  <div className="grid grid-cols-2 gap-3 bg-slate-50 p-3.5 rounded-lg text-xs">
                    <div>
                      <span className="text-slate-400 block font-medium">Base Premium</span>
                      <span className="text-sm font-bold text-slate-900">${prod.base_premium?.toFixed(2)}</span>
                    </div>
                    <div>
                      <span className="text-slate-400 block font-medium">Age Ceiling</span>
                      <span className="text-sm font-bold text-slate-900">{prod.min_applicant_age} - {prod.max_applicant_age} yrs</span>
                    </div>
                    <div className="col-span-2 pt-2 border-t border-slate-200/60">
                      <span className="text-slate-400 block font-medium">Coverage Limit Bounds</span>
                      <span className="text-xs font-bold text-brand-700 font-mono">
                        ${prod.min_coverage_limit?.toLocaleString()} – ${prod.max_coverage_limit?.toLocaleString()}
                      </span>
                    </div>
                  </div>

                  {/* Coverage Options */}
                  <div>
                    <h4 className="text-xs font-bold text-slate-900 uppercase tracking-wider mb-2 flex items-center gap-1.5">
                      <Layers className="w-3.5 h-3.5 text-brand-600" />
                      Standard Coverage Options ({prod.coverage_options?.length ?? 0})
                    </h4>
                    <div className="space-y-2">
                      {prod.coverage_options?.map((cov) => (
                        <div
                          key={cov.id}
                          className="p-2.5 bg-white border border-slate-100 rounded-lg shadow-2xs flex items-center justify-between text-xs hover:bg-slate-50/50"
                        >
                          <div>
                            <span className="font-semibold text-slate-800 block">{cov.name}</span>
                            <span className="text-[11px] text-slate-400">Limit: up to ${cov.max_limit?.toLocaleString()}</span>
                          </div>
                          <span className={`px-2 py-0.5 rounded text-[10px] font-bold ${
                            cov.coverage_category === 'CORE' ? 'bg-blue-50 text-blue-700' :
                            cov.coverage_category === 'OPTIONAL' ? 'bg-purple-50 text-purple-700' : 'bg-emerald-50 text-emerald-700'
                          }`}>
                            {cov.coverage_category}
                          </span>
                        </div>
                      ))}
                    </div>
                  </div>
                </div>

                {/* Footer Status */}
                <div className="px-6 py-3 bg-slate-50 border-t border-slate-100 flex items-center justify-between text-xs">
                  <span className="text-slate-500 font-medium">Underwriting Engine</span>
                  <span className="flex items-center gap-1 text-emerald-600 font-bold">
                    <Check className="w-3.5 h-3.5" /> Active in Pricing
                  </span>
                </div>
              </div>
            ))}
          </div>
        )}
      </div>
    </div>
  );
};
