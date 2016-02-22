##########################################################################
#                                                                        #
# Copyright (C) 2015 Carsten Fortmann-Grote                              #
# Contact: Carsten Fortmann-Grote <carsten.grote@xfel.eu>                #
#                                                                        #
# This file is part of simex_platform.                                   #
# simex_platform is free software: you can redistribute it and/or modify #
# it under the terms of the GNU General Public License as published by   #
# the Free Software Foundation, either version 3 of the License, or      #
# (at your option) any later version.                                    #
#                                                                        #
# simex_platform is distributed in the hope that it will be useful,      #
# but WITHOUT ANY WARRANTY; without even the implied warranty of         #
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the          #
# GNU General Public License for more details.                           #
#                                                                        #
# You should have received a copy of the GNU General Public License      #
# along with this program.  If not, see <http://www.gnu.org/licenses/>.  #
#                                                                        #
##########################################################################

""" Module that holds the PlasmaXRTSCalculatorParameters class.

    @author : CFG
    @institution : XFEL
    @creation 20151104

"""
import paths
import os
import numpy
import math
import tempfile
from scipy.constants import physical_constants
from scipy.constants import Avogadro
from SimEx.Utilities.Utilities import ALL_ELEMENTS
from SimEx.Utilities.EntityChecks import checkAndSetInstance
from SimEx.Utilities.EntityChecks import checkAndSetInteger
from SimEx.Utilities.EntityChecks import checkAndSetPositiveInteger
from SimEx.Utilities.EntityChecks import checkAndSetNonNegativeInteger


class PlasmaXRTSCalculatorParameters():
    """
    Class representing a x-ray free electron laser photon propagator.
    """

    def __init__(self,
                 elements=None,
                 scattering_angle=None,
                 electron_temperature=None,
                 electron_density=None,
                 ion_temperature=None,
                 ion_charge=None,
                 mass_density=None,
                 debye_temperature=None,
                 band_gap=None,
                 energy_range=None,
                 model_Sii=None,
                 model_See=None,
                 model_Sbf=None,
                 model_IPL=None,
                 model_Mix=None,
                 lfc=None,
                 Sbf_norm=None
                 ):

        """
        Constructor for the PlasmaXRTSCalculatorParameters.

        @params elements: The chemical elements in the scattering target.
        @type: List of [[element symbol, stochiometric number, charge], ...]
        @default: None
        @example: [['B', 1, 2], ['N', 1, 2]] for Boron-Nitride with both B and N two fold ionized (ion average).
        @example: [['C', 1, 4], ['H', 1, -1]] for Plastic with both four-fold ionized C and ionization of H calculated so that the given average ion charge comes out correct.

        @params scattering_angle: The scattering angle.
        @type: double
        @default: None

        @params electron_temperature: The temperature of the electron subsystems (units of eV).
        @type: double
        @default: None

        @params electron_density: The electron number density (units of 1/m^3)
        @type: double
        @default: None

        @params ion_temperature: The temperature of the ion subsystem (units of eV).
        @type: double
        @default: None

        @params ion_charge: The average ion charge (units of elementary charge e).
        @type: double
        @default: None

        @params mass_density: The mass density of the target (units of g/cm^3).
        @type: double
        @default: None

        @params debye_temperature: The Debye temperature (units of eV).
        @type: double
        @default: 0.0

        @params band_gap: The band gap of the target (units of eV).
        @type: double
        @default: 0.0

        @params energy_range: The energy range over which to calculate the scattering spectrum.
        @type: dict
        @default: [-10*wpl, 10*wpl, 0.1*wpl], wpl = electron plasma frequency.
        @example: {'min' : -100.0, 'max' : 100, 'step' : 0.5}



        @params model_Sii: The model to use for the ion-ion structure factor.
        @type: string or double
        @default: SOCP
        @example: model_Sii='DH' for the Debye-Hueckel structure factor.
        @example: model_Sii=1.5 to use a fixed value of Sii=1.5
        @note: Supported models are 'DH' (Debye-Hueckel), 'OCP' (one component plasma), 'SOCP' (screened one component plasma), 'SOCPN' (SOCP with negative screening Fourier component). Values >=0.0 are also allowed.


        @params model_See: The model of the dynamic (high frequency) part of the electron-electron structure factor.
        @type: string
        @default: RPA
        @note: Supported models are: 'RPA' (random phase approximation), 'BMA' (Mermin approximation with Born collision frequency), 'BMA+sLFC' (BMA with static local field correction).

        @params model_Sbf: The model for the
        @type: string
        @default: 'IA' (impulse approximation).
        @note: Supported are 'IA' (impulse approximation), 'FA' (form factor approximation).

        @params model_IPL: Model for ionization potential lowering.
        @type: string or double
        @default: SP (Stewart-Pyatt)
        @note: Supported are 'SP' (Stewart-Pyatt) and 'EK' (Eckard-Kroll). If a numeric value is given, this is interpreted as the ionization potential difference (lowering) in eV.

        @params model_Mix: The model to use for mixing (of species).
        @type: string
        @default: None

        @params lfc:  The local field correction to use.
        @type: double
        @default: 0.0 (calculate).

        @params Sbf_norm: How to normalize the bound-free structure factor.
        @type: string or double
        @default: None
        """

        # Check and set all parameters.
        self.__elements = checkAndSetElements(elements)
        self.__scattering_angle = checkAndSetScatteringAngle(scattering_angle)
        self.__electron_temperature = checkAndSetElectronTemperature(electron_temperature)
        # Set electron density, charge, and mass density depending on which input was given.
        self.__electron_density, self.__ion_charge, self.__mass_density = checkAndSetDensitiesAndCharge(electron_density, ion_charge, mass_density)
        self.__ion_temperature = checkAndSetIonTemperature(ion_temperature, self.electron_temperature)
        self.__debye_temperature = checkAndSetDebyeTemperature(debye_temperature)
        self.__band_gap = checkAndSetBandGap(band_gap)
        self.__energy_range = checkAndSetEnergyRange(energy_range, self.electron_density)
        self.__model_Sii = checkAndSetModelSii(model_Sii)
        self.__model_See = checkAndSetModelSee(model_See)
        self.__model_Sbf = checkAndSetModelSbf(model_Sbf)
        self.__model_IPL = checkAndSetModelIPL(model_IPL)
        self.__model_Mix = checkAndSetModelMix(model_Mix)
        self.__lfc = checkAndSetLFC(lfc)
        self.__Sbf_norm = checkAndSetSbfNorm(Sbf_norm)
        # Set state to not-initialized (e.g. input deck is not written).
        self.__is_initialized = False

    def _initialize(self):
        """ Initialize all parameters and io slots needed by the backengine. """

        # Make a temporary directory.
        self.__tmp_dir = tempfile.mkdtemp(prefix='xrs_')

        # Write the input file.
        input_deck_path = os.path.join( self.__tmp_dir, 'input.dat' )
        with open(input_deck_path, 'w') as input_deck:
            input_deck.write('--XRTS---input_file-----------------------------------\n')
            input_deck.write('--\n')
            input_deck.write('--fit_parameters------------------------------flag----\n')
            input_deck.write('DO_FIT                 0\n')
            input_deck.write('PHOTON_ENERGY %4.3f\n' % (self._input_data['photon_energy']))
            input_deck.write('SCATTERING_ANGLE     %4.3f\n' % (self.scattering_angle) )
            input_deck.write('ELECTRON_TEMP     %4.3f 0\n' % (self.electron_temperature) )
            input_deck.write('ELECTRON_DENSITY     %4.3e 0\n' % (self.electron_density) )
            input_deck.write('AMPLITUDE         1.0         0\n')
            input_deck.write('BASELINE             0.0         0\n')
            input_deck.write('Z_FREE             %4.3f        0\n' % (self.ion_charge) )
            input_deck.write('OUT(1=XSEC,2=PWR)    1\n')
            input_deck.write('--model_for_total_spec---------use-flag--------------\n')
            input_deck.write('USE_RPA %d\n' % (self.__use_rpa) )
            input_deck.write('USE_LINDHARD %d\n' % (self.__use_lindhard) )
            input_deck.write('USE_TSYTOVICH 0\n' )
            input_deck.write('USE_STATIC_LFC %d\n' % (self.__use_static_lfc) )
            input_deck.write('USE_DYNAMIC_LFC %d\n' % (self.__use_dynamic_lfc) )
            input_deck.write('USE_MFF %d\n' % (self.__use_mff) )
            input_deck.write('USE_BMA %d\n' % (self.__use_bma) )
            input_deck.write('USE_BMA+sLFC \n' % (self.__use_bma_slfc) )
            input_deck.write('USE_CORE 1\n')
            input_deck.write('--gradients------------------------------------------\n')
            input_deck.write('GRAD 0\n')
            input_deck.write('L_GRADIENT            0.0e-0        \n')
            input_deck.write('T_GRADIENT            0.0\n')
            input_deck.write('DSTEP                0.0    \n')
            input_deck.write('--ion_parameters----------------------------use_flag-\n')
            input_deck.write('ION_TEMP %d 1\n' % (self.ion_temperature) )
            input_deck.write('S_ION_FEATURE %4.3f %d\n' % (self.__Sii_value, self.__use_Sii_value) )
            input_deck.write('DEBYE_TEMP %4.3f %d\n' % (self.debye_temperature, self.__use_debye_temperature) )
            input_deck.write('BAND_GAP %4.3f %d\n' % (self.band_gap, self.__use_band_gap) )

            input_deck.write('--integration----------------------------------------\n')
            input_deck.write('N_DAWSON 32\n')
            input_deck.write('N_DISTRIBUTION 32\n')
            input_deck.write('N_PVI 32\n')
            input_deck.write('N_LANDEN 512\n')
            input_deck.write('N_RELAXATION 1024\n')
            input_deck.write('N_FFT 4096\n')
            input_deck.write('EPS 1.0E-4\n')
            input_deck.write('--See(k,w)------------------------------use/norm-----\n')
            input_deck.write('STATIC_MODEL(DH,OCP,SOCP,SOCPN) %s\n' % (self.model_Sii) )
            input_deck.write('USE_ADV_Mix %d\n' % (self.model_Mix) )
            input_deck.write('USE_IRS_MODEL                     0\n')
            input_deck.write('HARD_SPHERE_DIAM                 1E-10 0\n')
            input_deck.write('POLARIZABILITY                     0.0 0.0\n')
            input_deck.write('BOUND-FREE_MODEL(IA,IBA,FFA)     %s\n' % (self.model_Sbf) )
            input_deck.write('BOUND-FREE_NORM(FK,NO,USR)         %s     %d\n' % (self.Sbf_norm, self.__normalize_Sbf) )
            input_deck.write('BOUND-FREE_MEFF                 1.0\n')
            input_deck.write('USE_BOUND-FREE_DOPPLER          0\n')
            input_deck.write('CONT-LOWR_MODEL(SP,EK,USR)      %s\n' % (self.model_IPL) )
            input_deck.write('GK                         %4.3f 0\n')
            input_deck.write('RPA                         %d 0\n' % (self.__use_rpa) )
            input_deck.write('LINDHARD                     %d 0\n' % (self.__use_lindhard) )
            input_deck.write('SALPETER                         0 0\n')
            input_deck.write('LANDEN                         0 0\n')
            input_deck.write('RPA_TSYTOVICH                 0 0\n')
            input_deck.write('STATIC_LFC                     0 0\n')
            input_deck.write('DYNAMIC_LFC                     0 0\n')
            input_deck.write('MFF                             0 0\n')
            input_deck.write('BMA(+sLFC)                     %d 0\n' % (self.__write_bma))
            input_deck.write('CORE                             1 0\n')
            input_deck.write('TOTAL                         0 0\n')
            input_deck.write('E_MIN                         %4.3f\n' % (self.energy_range['min']))
            input_deck.write('E_MAX                         %4.3f\n' % (self.energy_range['max']))
            input_deck.write('E_STEP                         %4.3f\n' % (self.energy_range['step']))
            input_deck.write('--target_spec--------------------------chem----Zfree--\n')
            input_deck.write('NUMBER_OF_SPECIES %d\n' % (len(self.elements)) )
            for i,element in enumerate(self.elements.keys()):
                input_deck.write('TARGET_%d %s %d %d\n' % (i+1, element[0], element[1], element[2] ) )
            input_deck.write('MASS_DENSITY %4.3f\n' % (self.mass_density))
            input_deck.write('NE_ZF_LOCK %d\n' % (self.__lock_zf))
            input_deck.write('DATA_FILE data.txt\n')
            input_deck.write('NUMBER_POINTS 1024\n')
            input_deck.write('OPACITY_FILE nofile 0\n')
            input_deck.write('--instrument_function---------------------------------\n')
            input_deck.write('USE_FILE 0\n')
            input_deck.write('FILE_NAME nofile.dat\n')
            input_deck.write('INST_MODEL GAUSSIAN\n')
            input_deck.write('INST_FWHM 5.0\n')
            input_deck.write('BIN_PER_PIXEL 1.0\n')
            input_deck.write('INST_INDEX 2.0\n')
            input_deck.write('--additional_parameters-------------------------------\n')
            input_deck.write('MAX_ITERATIONS 0\n')
            input_deck.write('LEVENBERG_MARQUARDT 0\n')
            input_deck.write('SIGMA_LM 1.0\n')
            input_deck.write('SAVE_FILE xrts_out.txt\n')


    @property
    def elements(self):
        """ Query for the field data. """
        return self.__elements
    @elements.setter
    def elements(self, value):
        """ Set the elements to <value> """
        self.__elements = checkAndSetElements(value)

    @property
    def scattering_angle(self):
        """ Query for the scattering angle. """
        return self.__scattering_angle
    @scattering_angle.setter
    def scattering_angle(self, value):
        """ Set the scattering angle to <value>. """
        self.__scattering_angle = checkAndSetScatteringAngle(value)

    @property
    def electron_temperature(self):
        """ Query for the electron temperature. """
        return self.__electron_temperature
    @electron_temperature.setter
    def electron_temperature(self, value):
        """ Set the electron temperature to <value>. """
        self.__electron_temperature = checkAndSetElectronTemperature(value)

    @property
    def electron_density(self):
        """ Query for the electron density. """
        return self.__electron_density
    @electron_density.setter
    def electron_density(self, value):
        """ Set the electron density to <value>. """
        self.__electron_density = checkAndSetElectronDensity(value)

    @property
    def ion_temperature(self):
        """ Query for the ion temperature. """
        return self.__ion_temperature
    @ion_temperature.setter
    def ion_temperature(self, value):
        """ Set the ion temperature to <value>. """
        self.__ion_temperature = checkAndSetIonTemperature(value)

    @property
    def ion_charge(self):
        """ Query for the ion charge. """
        return self.__ion_charge
    @ion_charge.setter
    def ion_charge(self, value):
        """ Set the ion charge to <value>. """
        self.__ion_charge = checkAndSetIonCharge(value)

    @property
    def mass_density(self):
        """ Query for the mass density. """
        return self.__mass_density
    @mass_density.setter
    def mass_density(self, value):
        """ Set the mass density to <value>. """
        self.__mass_density = checkAndSetMassDensity(value)

    @property
    def debye_temperature(self):
        """ Query for the Debye temperature. """
        return self.__debye_temperature
    @debye_temperature.setter
    def debye_temperature(self, value):
        """ Set the Debye temperature to <value>. """
        self.__debye_temperature = checkAndSetDebyeTemperature(value)

    @property
    def band_gap(self):
        """ Query for the band gap. """
        return self.__band_gap
    @band_gap.setter
    def band_gap(self, value):
        """ Set the band gap to <value>. """
        self.__band_gap = checkAndSetBandGap(value)

    @property
    def energy_range(self):
        """ Query for the energy range. """
        return self.__energy_range
    @energy_range.setter
    def energy_range(self, value):
        """ Set the energy range to <value>. """
        self.__energy_range = checkAndSetEnergyRange(value)

    @property
    def model_Sii(self):
        """ Query for the ion-ion structure factor model. """
        return self.__model_Sii
    @model_Sii.setter
    def model_Sii(self, value):
        """ Set the ion-ion structure factor model to <value>. """
        self.__model_Sii = checkAndSetModelSii(value)

    @property
    def model_See(self):
        """ Query for the electron-electron (high-frequency) structure factor model. """
        return self.__model_See
    @model_See.setter
    def model_See(self, value):
        """ Set the electron-electron (high-frequency) structure factor model to <value>. """
        self.__model_See = checkAndSetModelSee(value)

    @property
    def model_Sbf(self):
        """ Query for the bound-free structure factor model. """
        return self.__model_Sbf
    @model_Sbf.setter
    def model_Sbf(self, value):
        """ Set the bound-free structure factor model to <value>. """
        self.__model_Sbf = checkAndSetModelSbf(value)

    @property
    def model_IPL(self):
        """ Query for the ionization potential lowering model. """
        return self.__model_IPL
    @model_IPL.setter
    def model_IPL(self, value):
        """ Set the ionization potential lowering model to <value>. """
        self.__model_IPL = checkAndSetModelIPL(value)

    @property
    def model_Mix(self):
        """ Query for the mixing model. """
        return self.__model_Mix
    @model_Mix.setter
    def model_Mix(self, value):
        """ Set the mixing model to <value>. """
        self.__model_Mix = checkAndSetModelMix(value)

    @property
    def lfc(self):
        """ Query for the local field factor. """
        return self.__lfc
    @lfc.setter
    def lfc(self, value):
        """ Set the local field factor to <value>. """
        self.__lfc = checkAndSetLFC(value)

    @property
    def Sbf_norm(self):
        """ Query for the norm of the bound-free structure factor. """
        return self.__Sbf_norm
    @Sbf_norm.setter
    def Sbf_norm(self, value):
        """ Set the norm of the bound-free structure factor to <value>. """
        self.__Sbf_norm = checkAndSetSbfNorm(value)

    #@property
    #def (self):
        #""" Query for the <++>. """
        #return self.__<++>

    #@property
    #def <++>(self):
        #""" Query for the <++>. """
        #return self.__<++>

    #@property
    #def <++>(self):
        #""" Query for the <++>. """
        #return self.__<++>

    #@property
    #def <++>(self):
        #""" Query for the <++>. """
        #return self.__<++>

    #@property
    #def <++>(self):
        #""" Query for the <++>. """
        #return self.__<++>

    #@property
    #def <++>(self):
        #""" Query for the <++>. """
        #return self.__<++>
###########################
# Check and set functions #
###########################
def checkAndSetScatteringAngle(angle):
    """
    Utility to check if the scattering angle is in the correct range.
    @param angle : The angle to check.
    @return The checked angle.
    @raise ValueError if not 0 <= angle <= 180
    """

    # Set default.
    if angle is None:
        raise RuntimeError( "Scattering angle not specified.")

    # Check if in range.
    if angle <= 0.0 or angle > 180.0:
        raise( ValueError, "Scattering angle must be between 0 and 180 [degrees].")

    # Return.
    return angle

def checkAndSetElements(elements):
    """ Utility to check if input is a valid list of elements.

    @param  elements : The elements to check.
    @type : list
    @return : The checked list of elements.
    """

    if elements is None:
        raise RuntimeError( "No element(s) specified. Give at least one chemical element.")
    elements = checkAndSetInstance( list, elements, None )

    # Check each element.
    for element in elements:
        symbol, stoch, chrg = checkAndSetInstance( list, element, None )
        if symbol not in ALL_ELEMENTS:
            raise ValueError( '%s is not a valid chemical element symbol.' % (symbol) )
        stoch = checkAndSetPositiveInteger(stoch)
        chrg = checkAndSetInteger(chrg)
        if chrg < -1:
            raise ValueError( "Charge must be >= -1.")

        element = [symbol, stoch, chrg]
    return elements

def checkAndSetElectronTemperature(electron_temperature):
    """ Utility to check if input is a valid electron temperature.

    @param  electron_temperature : The electron temperature to check.
    @type : double
    @return : The checked electron temperature.
    """
    if electron_temperature is None:
        raise RuntimeError( "Electron temperature not specified.")
    electron_temperature = checkAndSetInstance( float, electron_temperature, None)
    if electron_temperature <= 0.0:
        raise ValueError( "Electron temperature must be positive.")

    return electron_temperature

def checkAndSetDensitiesAndCharge(electron_density, ion_charge, mass_density):
    """ Utility to check input and return a set of consistent electron density, average ion charge, and mass density, if two are given as input.
    """
    # Find number of Nones in input.
    number_of_nones = (sum(x is None for x in [electron_density, ion_charge, mass_density]))
    # raise if not enough input.
    if number_of_nones > 1:
        raise RuntimeError( "At least two of electron_density, ion_charge, and mass_density must be given.")

    if electron_density is None:
        electron_density = mass_density * ion_charge * Avogadro* 1e6
    if ion_charge is None:
        ion_charge = electron_density / (mass_density * Avogadro* 1e6)
    if mass_density is None:
        mass_density = electron_density / (ion_charge * Avogadro* 1e6)

    if abs( electron_density / (mass_density * ion_charge * Avogadro* 1e6) - 1 ) > 1e-4:
        raise ValueError( "Electron density, mass_density, and ion charge are not internally consistent: ne = %5.4e/m**3, rho*Zf*NA = %5.4e/m**3." % (electron_density, mass_density * ion_charge * Avogadro* 1e6) )

    return electron_density, ion_charge, mass_density

def checkAndSetIonTemperature(ion_temperature, electron_temperature=None):
    """ Utility to check if input is a valid ion temperature.

    @param  ion_temperature : The ion temperature to check.
    @type : double
    @default : Electron temperature.
    @return : The checked ion temperature.
    """
    if electron_temperature is None:
        if ion_temperature is None:
            raise RuntimeError(" Could not fix ion temperature because electron temperature not given.")
    ion_temperature = checkAndSetInstance( float, ion_temperature, electron_temperature)
    if ion_temperature <= 0.0:
        raise ValueError( "Ion temperature must be positive.")

    return ion_temperature

def checkAndSetDebyeTemperature(debye_temperature):
    """ Utility to check if input is a valid Debye temperature.

    @param  debye_temperature : The Debye temperature to check.
    @type : double
    @default : 0.0
    @return : The checked Debye temperature.
    """
    debye_temperature = checkAndSetInstance( float, debye_temperature, 0.0)
    if debye_temperature < 0.0:
        raise ValueError( "Debye temperature must be non-negative.")

    return debye_temperature

def checkAndSetBandGap(band_gap):
    """ Utility to check if input is a valid bandgap.

    @param  band_gap: The bandgap to check.
    @type : double
    @default 0.0.
    @return : The checked bandgap.
    """
    band_gap = checkAndSetInstance( float, band_gap, 0.0)
    if band_gap < 0.0:
        raise ValueError( "Debye temperature must be positive.")

    return band_gap

def checkAndSetModelMix(model_Mix):
    """ Utility to check if input is a valid mixing model.

    @param  model_Mix : The mixing model to check.
    @type : string
    @return : The checked mixing model.
    """
    if isinstance( model_Mix, str):
        model_Mix = model_Mix.lower()
    if model_Mix not in ['adv', None]:
        raise ValueError('The mixing model has to be "ADV" (advanced) or None.')

    return {'adv' : 1, None: 0}[model_Mix]

def checkAndSetLFC(lfc):
    """ Utility to check if input is a valid local field correction factor.

    @param  lfc : The lfc to check.
    @type : double
    @return : The checked lfc.
    """
    lfc = checkAndSetInstance(float, lfc, 0.0)

    return lfc

def checkAndSetSbfNorm(Sbf_norm):
    """ Utility to check if input is a valid norm of the bound-free structure factor.

    @param  Sbf_norm : The norm to check.
    @type : string or double.
    @return : The checked norm.
    """
    if Sbf_norm not in ['FK', 'NO', None] and not isinstance( Sbf_norm, float ):
        raise ValueError('The bound-free norm parameter has to be "FK", "NO", None, or a numerical value.')
    return Sbf_norm

def checkAndSetEnergyRange(energy_range, electron_density):
    """
    Utility to check if the photon energy range is ok.
    @param energy_range : The range to check.
    @type dict
    @return The checked photon energy range.
    @raise ValueError if not of correct shape.
    """
    # Some constants.
    bohr_radius_m = physical_constants['Bohr radius'][0]
    rydberg_energy_eV = physical_constants['Rydberg constant times hc in eV'][0]

    # Get plasma frequency.
    plasma_frequency_eV = 4. * math.sqrt( electron_density * (bohr_radius_m * 1e2)**3 * math.pi) * rydberg_energy_eV

    # Set to +/- 10*wpl if no range given.
    energy_range_default = {'min' : -10.*plasma_frequency_eV, 'max' : 10.*plasma_frequency_eV, 'step':0.1*plasma_frequency_eV}
    energy_range = checkAndSetInstance( dict, energy_range, energy_range_default)

    # Return
    return energy_range

def checkAndSetModelSii( model ):
    """
    Utility to check if the model is a valid model for the Rayleigh (quasistatic) scattering feature.

    @param model : The model to check.
    @type : str
    @return : The checked model
    @raise ValueError if not a string or not a valid Sii model ('RPA', 'DH',
    """

    if model is None:
        model = 'SOCP'

    ###TODO: Complete
    valid_models = [ 'DH', 'OCP', 'SOCP', 'SOCPN' ]

    if not (model in valid_models or not isinstance( model, float )):
        raise ValueError( "The Sii model must be a valid Sii model or a numerical value. Valid Sii models are %s." % (str(valid_models)) )

    return model


def checkAndSetModelSee( model ):
    """
    Utility to check if the model is a valid model for the high frequency (dynamic) feature.

    @param model : The model to check.
    @type : str
    @return : The checked model
    @raise ValueError if not a string or not a valid See0 model ('RPA', 'BMA', 'BMA+sLFC', 'BMA+dLFC', 'LFC', 'Landen')
    """

    # Default handling.
    model = checkAndSetInstance( str, model, 'RPA')

    # Valid models.
    valid_models = ['RPA',
                    'Lindhard',
                    'static LFC',
                    'dynamic LFC',
                    'BMA',
                    'BMA+sLFC',
                    'BMA+dLFC',
                    ]

    if model not in valid_models:
        raise ValueError( "The See model must be a valid See0 model. Valid See0 models are %s." % (str(valid_models)) )

    # Return
    return model

def checkAndSetModelSbf( model ):
    """
    Utility to check if the model is a valid model for the bound-free (Compton) scattering feature.

    @param model : The model to check.
    @type : str
    @return : The checked model
    @raise ValueError if not a string or not a valid Sbf model ('IA', 'HWF')
    """

    # Handle default.
    model = checkAndSetInstance( str, model, 'IA')

    valid_models = ['IA',
                    'IBA',
                    'FFA'
                    ]

    if model not in valid_models:
        raise ValueError( "The Sbf model must be a valid Sbf model. Valid Sbf models are %s." % (str(valid_models)) )

    # Return
    return model

def checkAndSetModelIPL( model ):
    """
    Utility to check if the model is a valid model for ionization potential lowering.

    @param model : The model to check.
    @type : str or float
    @return : The checked model
    @raise ValueError if not a valid IPL model.
    """

    # Handle default.
    if model is None:
        model = 'SP'

    valid_models = ['SP',
                    'EK',
                    ]

    if not (model in valid_models or not isinstance( model, float )):
        raise ValueError( "The Sbf model must be a valid Sbf model. Valid Sbf models are %s or a numerical value." % (str(valid_models)) )

    # Return
    return model


