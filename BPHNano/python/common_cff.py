import FWCore.ParameterSet.Config as cms
from PhysicsTools.NanoAOD.common_cff import *

def ufloat(expr, precision = -1, doc = ''):
  return Var('userFloat("%s")' % expr, 
             float, precision = precision, doc = doc)

def uint(expr, doc = ''):
  return Var('userInt("%s")' % expr, int, doc = doc)

def ubool(expr, precision = -1, doc = ''):
  return Var('userInt("%s") == 1' % expr, bool, doc = doc)

def full_precision_p4(table):
  """Store a table's eta/phi/mass at full float precision.

  The central CandVars keeps mass at 10 and eta/phi at 12 mantissa bits: 0.49 MeV mass steps
  below 1 GeV make a comb in any fine mass histogram, and eta/phi steps of up to 0.5 mrad put
  a ~10% error on a few-MeV pair mass (conversion, Dalitz pair) rebuilt offline from its legs.
  """
  for v in ('eta', 'phi', 'mass'):
    if hasattr(table.variables, v):
      getattr(table.variables, v).precision = cms.int32(-1)
  return table
