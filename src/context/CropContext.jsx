import React, { createContext, useCallback, useContext, useEffect, useMemo, useRef, useState } from 'react';

const CropContext = createContext(null);

const CROP_USER_ID = 'demo_user';
const PLANS_ENDPOINT = `http://127.0.0.1:8000/crop-plan/user/${CROP_USER_ID}`;
const PLAN_DETAILS_ENDPOINT = (planId) => `http://127.0.0.1:8000/crop-plan/${planId}`;

const getStoredPlanId = () => {
  try {
    return localStorage.getItem('selectedCropPlanId');
  } catch {
    return null;
  }
};

const storePlanId = (planId) => {
  try {
    if (planId) {
      localStorage.setItem('selectedCropPlanId', planId);
    } else {
      localStorage.removeItem('selectedCropPlanId');
    }
  } catch {
    // ignore storage errors
  }
};

export function CropProvider({ children }) {
  const [plans, setPlans] = useState([]);
  const [selectedPlanId, setSelectedPlanId] = useState(getStoredPlanId());
  const [planDetails, setPlanDetails] = useState({});
  const [loadingPlans, setLoadingPlans] = useState(false);
  const [error, setError] = useState(null);
  const loadingPlanIds = useRef(new Set());

  const refreshPlans = useCallback(async () => {
    setLoadingPlans(true);
    setError(null);

    try {
      const response = await fetch(PLANS_ENDPOINT);
      if (!response.ok) {
        throw new Error('Failed to fetch crop plans');
      }
      const data = await response.json();
      const nextPlans = data.plans || [];
      setPlans(nextPlans);

      if (!selectedPlanId && nextPlans.length > 0) {
        setSelectedPlanId(nextPlans[0].id);
        storePlanId(nextPlans[0].id);
      }
    } catch (err) {
      setError(err.message || 'Failed to fetch crop plans');
    } finally {
      setLoadingPlans(false);
    }
  }, [selectedPlanId]);

  useEffect(() => {
    refreshPlans();
  }, [refreshPlans]);

  const selectPlan = useCallback((planId) => {
    setSelectedPlanId(planId);
    storePlanId(planId);
  }, []);

  const ensurePlanDetails = useCallback(async (planId) => {
    if (!planId || planDetails[planId] || loadingPlanIds.current.has(planId)) {
      return;
    }

    loadingPlanIds.current.add(planId);
    try {
      const response = await fetch(PLAN_DETAILS_ENDPOINT(planId));
      if (!response.ok) {
        throw new Error('Failed to fetch plan details');
      }
      const data = await response.json();
      setPlanDetails((prev) => ({
        ...prev,
        [planId]: data,
      }));
    } catch (err) {
      setError(err.message || 'Failed to fetch plan details');
    } finally {
      loadingPlanIds.current.delete(planId);
    }
  }, [planDetails]);

  const removePlan = useCallback((planId) => {
    setPlans((prev) => prev.filter((plan) => plan.id !== planId));
    setPlanDetails((prev) => {
      const next = { ...prev };
      delete next[planId];
      return next;
    });
    if (selectedPlanId === planId) {
      setSelectedPlanId(null);
      storePlanId(null);
    }
  }, [selectedPlanId]);

  const selectedPlan = useMemo(() => plans.find((plan) => plan.id === selectedPlanId) || null, [plans, selectedPlanId]);
  const selectedPlanDetails = useMemo(() => (selectedPlanId ? planDetails[selectedPlanId] || null : null), [planDetails, selectedPlanId]);

  const value = useMemo(() => ({
    plans,
    planDetails,
    selectedPlanId,
    selectedPlan,
    selectedPlanDetails,
    loadingPlans,
    error,
    setPlans,
    refreshPlans,
    selectPlan,
    ensurePlanDetails,
    removePlan,
  }), [plans, planDetails, selectedPlanId, selectedPlan, selectedPlanDetails, loadingPlans, error, setPlans, refreshPlans, selectPlan, ensurePlanDetails, removePlan]);

  return (
    <CropContext.Provider value={value}>
      {children}
    </CropContext.Provider>
  );
}

export function useCropContext() {
  const context = useContext(CropContext);
  if (!context) {
    throw new Error('useCropContext must be used within CropProvider');
  }
  return context;
}
