from flask import Flask, request, jsonify
from flask_cors import CORS
from flask_limiter import Limiter
import os
import requests
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

app = Flask(__name__)
CORS(app)

# Configuration
API_KEY = os.getenv("OPENROUTER_API_KEY")
if not API_KEY:
    raise ValueError("OpenRouter API key not found. Set OPENROUTER_API_KEY in .env")

API_URL = "https://openrouter.ai/api/v1/chat/completions"

# CFD keywords
CFD_KEYWORDS = [keyword.lower() for keyword in [
    "CFD", "Navier-Stokes equations", "openfoam", "Reynolds-Averaged Navier-Stokes (RANS)", 
    "Large Eddy Simulation (LES)", "Direct Numerical Simulation (DNS)", "RANS", "LES",
    "Euler equations", "Boussinesq approximation", "Continuity equation",
    "Momentum equation", "Energy equation", "Species transport equation",
    "Incompressible flow", "Compressible flow", "Ideal gas law", "cfd",
    "k", "epsilon", "kepsilon", "k-epsilon", "k-epsilon model", "SST k-omega", 
    "Spalart-Allmaras", "Reynolds Stress Model (RSM)", "Detached Eddy Simulation (DES)",
    "Wall functions", "Eddy viscosity", "Turbulent kinetic energy", "Dissipation rate", 
    "Inlet turbulence intensity", "yPlus value", "Van Driest damping", "Log-law layer",
    "Finite Volume Method (FVM)", "Finite Element Method (FEM)", "Finite Difference Method (FDM)",
    "Discretization schemes", "Central differencing", "Upwind scheme", "QUICK scheme",
    "Pressure-Implicit Split-Operator (PISO)", "SIMPLE algorithm", "Transient simulation",
    "Steady-state simulation", "Multiphase flow", "VOF method", "Level Set method", 
    "Adaptive mesh refinement", "OpenFOAM", "ANSYS Fluent", "COMSOL Multiphysics", 
    "STAR-CCM+", "SU2", "Autodesk CFD", "CONVERGE", "ParaView", "Tecplot", "Pointwise", 
    "ICEM CFD", "Gmsh", "snappyHexMesh", "blockMesh", "Salome", "CFX-Pre", "Fluent Meshing",
    "ANSYS", "Ansys", "fluent", "Structured mesh", "Unstructured mesh", "Hexahedral elements",
    "Tetrahedral elements", "Polyhedral mesh", "Boundary layer mesh", "Mesh independence",
    "Skewness", "Orthogonality", "Aspect ratio", "Sliver cells", "Non-conformal mesh",
    "O-grid topology", "Inflation layers", "Mesh convergence", "Grid generation", 
    "Velocity inlet", "Pressure outlet", "No-slip wall", "Symmetry plane", "Periodic boundary",
    "Mass flow inlet", "Outflow", "Far-field", "Adiabatic wall", "Heat flux boundary", 
    "Moving mesh", "Sliding mesh", "Rotating reference frame", "Interface conditions", 
    "Non-reflective BC", "Streamlines", "Vorticity", "Q-criterion", "Pressure coefficient",
    "Drag coefficient", "Lift coefficient", "Nusselt number", "Residual plots", "Contour plots",
    "Vector fields", "Pathlines", "Streaklines", "Isosurfaces", "Cut planes", "Volume rendering",
    "Boundary layer separation", "Shock waves", "Vortex shedding", "Cavitation", 
    "Thermal convection", "Natural convection", "Forced convection", "Laminar-turbulent transition",
    "Flow separation", "Wake region", "Recirculation zones", "Swirl flow", "Dean vortices",
    "Rayleigh-Bénard convection", "Taylor-Couette flow", "Combustion modeling", 
    "Radiation heat transfer", "Discrete Phase Model (DPM)", "Species transport", "Multiphase flow",
    "Eulerian-Eulerian approach", "Lagrangian particle tracking", "Acoustics simulation",
    "MagnetoHydroDynamics (MHD)", "Plasma flow", "Non-Newtonian fluids", "Porous media", 
    "Slurry flow", "Grid convergence index", "Richardson extrapolation", "Benchmark cases",
    "Lid-driven cavity", "Backward-facing step", "Ahmed body", "NASA Turbulence Modeling Resource",
    "DRAGON challenge", "HPC validation", "Experimental correlation", "Uncertainty quantification",
    "High Performance Computing (HPC)", "MPI parallelization", "OpenMP", "GPU acceleration",
    "Cloud computing", "Cluster computing", "Load balancing", "Domain decomposition", 
    "Scalability testing", "Adjoint optimization", "Genetic algorithms", "Gradient-based methods",
    "Shape optimization", "Topology optimization", "Surrogate modeling", "Design of Experiments (DOE)",
    "Parameter sweep", "Sensitivity analysis", "Aerodynamic drag reduction", "HVAC system design",
    "Wind load analysis", "Turbomachinery design", "Internal combustion engines", "Aeroacoustics",
    "Marine hydrodynamics", "Biomedical flows", "Electrochemical flow cells", "Mixing tanks",
    "Pipe flow analysis", "Heat exchanger design", "fluent", "boundary", "conditions", "what is Ansys",
    "Immersed boundary method", "Lattice Boltzmann Method (LBM)", "Smoothed Particle Hydrodynamics (SPH)",
    "Discontinuous Galerkin", "Arbitrary Lagrangian-Eulerian (ALE)", "Overset meshes", 
    "Dynamic mesh handling", "Fluid-Structure Interaction (FSI)", "Conjugate heat transfer", 
    "Phase change modeling", "Dynamic viscosity", "Kinematic viscosity", "Thermal conductivity",
    "Specific heat capacity", "Prandtl number", "Reynolds number", "Mach number", "Froude number",
    "Strouhal number", "Knudsen number", "Nusselt number", "Biot number", "Sherwood number",
    "STL files", "CGNS format", "Fluent .cas/.dat", "OpenFOAM case files", "Ensight Gold", "PLOT3D",
    "Gmsh .msh", "VTK format", "HDF5", "Stream function", "Vorticity magnitude", "Helicity",
    "Lambda2 criterion", "Vortex cores", "Shear stress visualization", "Pressure gradient",
    "Velocity magnitude", "Turbulence intensity", "Residual monitors", "Force coefficients",
    "Torque calculation", "Negative volume cells", "High skewness cells", "Non-convergence",
    "Divergence detected", "Floating point exception", "Courant number", "Time step stability",
    "Under-relaxation factors", "Residual targets", "Digital twins", "Machine learning in CFD",
    "AI-driven meshing", "Reduced Order Models (ROM)", "Unsteady RANS (URANS)", "LES-WMLES",
    "Hybrid RANS-LES", "Scale-resolving simulations", "Quantum CFD", "what is Ansys", "How it works",
    "Explain in detail", "explain more", "ansys", "Ansys", "flow", "cam", "CAM", "finite element"
]]

CFD_KEYWORDS_SET = set(CFD_KEYWORDS)

@app.route('/')
def home():
    return "CFD Chatbot Backend - Use POST /ask for queries"

limiter = Limiter(app=app, key_func=lambda: request.remote_addr)
@app.route('/ask', methods=['POST'])
@limiter.limit("10/minute")  # Prevent abuse
def ask():
    try:
        data = request.get_json()
        app.logger.info(f"Received data: {data}")  # Log incoming data
        user_question = data.get('question', '').lower()
        
        if not any(keyword in user_question for keyword in CFD_KEYWORDS_SET):
            app.logger.warning("Non-CFD question detected")  # Log keyword check failure
            return jsonify({"error": "CFD-related questions only"}), 400

        # OpenRouter required headers
        headers = {
            "Authorization": f"Bearer {API_KEY}",
            "Content-Type": "application/json",
            "HTTP-Referer": "http://localhost:5000",  # Required by OpenRouter
            "X-Title": "CFD Assistant"  # Identifier for your app
        }

        payload = {
            "model": "google/gemini-2.0-flash-thinking-exp:free",
            "messages": [{"role": "user", "content": user_question}],
            "temperature": 0.7
        }

        response = requests.post(API_URL, json=payload, headers=headers)
        app.logger.info(f"OpenRouter Response: {response.text}")
        
        if response.status_code != 200:
            app.logger.error(f"API request failed with status {response.status_code}: {response.text}")
            return jsonify({"error": f"API request failed: {response.text}"}), 500

        response_data = response.json()
        app.logger.info(f"Parsed response data: {response_data}")
        
        # Handle OpenRouter response format
        if 'choices' in response_data and len(response_data['choices']) > 0:
            answer = response_data['choices'][0].get('message', {}).get('content', 'No content found')
            return jsonify({"answer": answer})
        else:
            app.logger.error(f"Unexpected API response format: {response_data}")
            return jsonify({"error": "Unexpected API response format"}), 500

    except requests.exceptions.RequestException as e:
        app.logger.error(f"Network error: {str(e)}")
        return jsonify({"error": f"Network error: {str(e)}"}), 500
    except Exception as e:
        app.logger.error(f"Server error: {str(e)}")
        return jsonify({"error": f"Server error: {str(e)}"}), 500

if __name__ == '__main__':
    if not os.path.exists('.env'):
        raise RuntimeError("Missing .env file")
    app.run(host='0.0.0.0', port=5000, debug=True, use_reloader=False)