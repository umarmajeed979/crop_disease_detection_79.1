"""
Disease Information Database
Comprehensive disease and pest information
"""

from typing import Optional, Dict
from app.utils.logger import get_logger

logger = get_logger(__name__)


class DiseaseDatabase:
    """Disease and pest information database"""
    
    def __init__(self):
        self.diseases = self._load_disease_data()
        self.pests = self._load_pest_data()
    
    def _load_disease_data(self) -> Dict:
        """Load disease information"""
        return {
            # TOMATO DISEASES
            "tomato_early_blight": {
                "name": "Tomato Early Blight",
                "crop": "Tomato",
                "type": "disease",
                "pathogen": "Alternaria solani (Fungus)",
                "symptoms": [
                    "Dark brown spots with concentric rings on older leaves",
                    "Yellowing around spots",
                    "Leaf drop starting from bottom",
                    "Stem lesions with dark, sunken areas"
                ],
                "severity_indicators": {
                    "mild": "Few spots on lower leaves only",
                    "moderate": "Multiple spots on lower and middle leaves",
                    "severe": "Extensive leaf damage, defoliation, stem lesions"
                },
                "treatment": {
                    "organic": [
                        "Remove and destroy infected leaves immediately",
                        "Apply neem oil spray (3-5 ml per liter water) weekly",
                        "Use copper-based fungicides (2g per liter)",
                        "Improve air circulation by proper spacing"
                    ],
                    "chemical": [
                        "Mancozeb 75% WP (2-2.5g per liter)",
                        "Chlorothalonil (2ml per liter)",
                        "Azoxystrobin (1ml per liter)"
                    ]
                },
                "prevention": [
                    "Use disease-resistant varieties",
                    "Rotate crops (3-4 year cycle)",
                    "Mulch to prevent soil splash",
                    "Water at base, avoid wetting leaves",
                    "Maintain proper plant spacing"
                ],
                "optimal_spray_schedule": "Every 7-10 days during wet weather"
            },
            
            "tomato_late_blight": {
                "name": "Tomato Late Blight",
                "crop": "Tomato",
                "type": "disease",
                "pathogen": "Phytophthora infestans (Oomycete)",
                "symptoms": [
                    "Water-soaked spots on leaves",
                    "White fuzzy growth on leaf undersides",
                    "Rapid blackening and death of foliage",
                    "Brown lesions on stems",
                    "Fruit rot with greasy appearance"
                ],
                "treatment": {
                    "organic": [
                        "Remove and burn infected plants immediately",
                        "Copper hydroxide (3g per liter water)",
                        "Improve drainage",
                        "Avoid overhead irrigation"
                    ],
                    "chemical": [
                        "Metalaxyl + Mancozeb (2.5g per liter)",
                        "Cymoxanil + Mancozeb (2g per liter)",
                        "Dimethomorph (1ml per liter)"
                    ]
                },
                "prevention": [
                    "Use certified disease-free seeds",
                    "Plant resistant varieties",
                    "Avoid planting near potato fields",
                    "Ensure good air circulation"
                ]
            },
            
            "tomato_bacterial_spot": {
                "name": "Tomato Bacterial Spot",
                "crop": "Tomato",
                "type": "disease",
                "pathogen": "Xanthomonas spp. (Bacteria)",
                "symptoms": [
                    "Small dark brown spots on leaves",
                    "Spots may have yellow halos",
                    "Fruit spots are raised and corky",
                    "Severe defoliation in humid conditions"
                ],
                "treatment": {
                    "organic": [
                        "Copper-based bactericides",
                        "Remove infected plant parts",
                        "Improve air circulation"
                    ],
                    "chemical": [
                        "Copper hydroxide + Mancozeb",
                        "Streptomycin sulfate (where approved)"
                    ]
                }
            },
            
            "tomato_leaf_mold": {
                "name": "Tomato Leaf Mold",
                "crop": "Tomato",
                "type": "disease",
                "pathogen": "Passalora fulva (Fungus)",
                "symptoms": [
                    "Pale green to yellow spots on upper leaf surface",
                    "Olive-green to brown velvety growth on undersides",
                    "Leaves curl and wither",
                    "No fruit spots typically"
                ],
                "treatment": {
                    "organic": [
                        "Increase ventilation and reduce humidity",
                        "Remove infected leaves",
                        "Neem oil or sulfur sprays"
                    ],
                    "chemical": [
                        "Chlorothalonil",
                        "Mancozeb",
                        "Copper fungicides"
                    ]
                }
            },
            
            "tomato_septoria_leaf_spot": {
                "name": "Tomato Septoria Leaf Spot",
                "crop": "Tomato",
                "type": "disease",
                "pathogen": "Septoria lycopersici (Fungus)",
                "symptoms": [
                    "Small circular spots with gray centers",
                    "Dark brown margins",
                    "Tiny black dots (fruiting bodies) in spot centers",
                    "Lower leaves affected first"
                ],
                "treatment": {
                    "organic": [
                        "Remove infected leaves",
                        "Mulch to prevent splash",
                        "Copper fungicides"
                    ],
                    "chemical": [
                        "Chlorothalonil",
                        "Mancozeb",
                        "Azoxystrobin"
                    ]
                }
            },
            
            "tomato_target_spot": {
                "name": "Tomato Target Spot",
                "crop": "Tomato",
                "type": "disease",
                "pathogen": "Corynespora cassiicola (Fungus)",
                "symptoms": [
                    "Brown spots with concentric rings",
                    "Can affect leaves, stems, and fruit",
                    "Spots may coalesce",
                    "Severe defoliation possible"
                ],
                "treatment": {
                    "organic": [
                        "Remove infected tissues",
                        "Improve air circulation",
                        "Copper sprays"
                    ],
                    "chemical": [
                        "Azoxystrobin",
                        "Chlorothalonil",
                        "Mancozeb"
                    ]
                }
            },
            
            "tomato_mosaic_virus": {
                "name": "Tomato Mosaic Virus",
                "crop": "Tomato",
                "type": "disease",
                "pathogen": "Tomato mosaic virus (Virus)",
                "symptoms": [
                    "Mottled light and dark green on leaves",
                    "Leaf distortion and curling",
                    "Stunted growth",
                    "Reduced fruit yield and quality"
                ],
                "treatment": {
                    "organic": [
                        "Remove and destroy infected plants",
                        "Control aphids and other vectors",
                        "Use virus-free seeds"
                    ],
                    "chemical": [
                        "No chemical cure - focus on prevention",
                        "Insecticides for vector control"
                    ]
                },
                "prevention": [
                    "Use resistant varieties",
                    "Sanitize tools",
                    "Wash hands after handling tobacco",
                    "Remove infected plants immediately"
                ]
            },
            
            "tomato_yellow_leaf_curl_virus": {
                "name": "Tomato Yellow Leaf Curl Virus",
                "crop": "Tomato",
                "type": "disease",
                "pathogen": "Begomovirus (Virus)",
                "symptoms": [
                    "Upward curling of leaf margins",
                    "Yellowing between leaf veins",
                    "Stunted plant growth",
                    "Reduced or no fruit production"
                ],
                "treatment": {
                    "organic": [
                        "Remove infected plants",
                        "Control whitefly vectors",
                        "Use reflective mulches"
                    ],
                    "chemical": [
                        "Systemic insecticides for whitefly control",
                        "Imidacloprid",
                        "Thiamethoxam"
                    ]
                }
            },
            
            "tomato_spider_mites": {
                "name": "Two-Spotted Spider Mite",
                "crop": "Tomato",
                "type": "pest",
                "pathogen": "Tetranychus urticae (Arachnid)",
                "symptoms": [
                    "Fine webbing on leaves",
                    "Stippling or bronzing of leaves",
                    "Yellow or brown spots",
                    "Leaf drop in severe cases"
                ],
                "treatment": {
                    "organic": [
                        "Strong water spray to dislodge",
                        "Neem oil (5ml per liter)",
                        "Insecticidal soap",
                        "Release predatory mites"
                    ],
                    "chemical": [
                        "Abamectin",
                        "Spiromesifen",
                        "Bifenthrin"
                    ]
                }
            },
            
            "tomato_healthy": {
                "name": "Healthy Tomato",
                "crop": "Tomato",
                "type": "healthy",
                "pathogen": "None",
                "symptoms": [
                    "Vibrant green leaves",
                    "No spots or discoloration",
                    "Uniform leaf color",
                    "Strong, upright growth"
                ],
                "treatment": {
                    "organic": ["Continue regular care"],
                    "chemical": ["No treatment needed"]
                },
                "prevention": [
                    "Maintain current practices",
                    "Regular monitoring",
                    "Proper nutrition and watering"
                ]
            },
            
            # POTATO DISEASES
            "potato_early_blight": {
                "name": "Potato Early Blight",
                "crop": "Potato",
                "type": "disease",
                "pathogen": "Alternaria solani (Fungus)",
                "symptoms": [
                    "Dark brown spots with concentric rings",
                    "Lower leaves affected first",
                    "Yellowing around lesions",
                    "Premature defoliation"
                ],
                "treatment": {
                    "organic": [
                        "Remove infected foliage",
                        "Copper fungicides",
                        "Improve air circulation"
                    ],
                    "chemical": [
                        "Mancozeb",
                        "Chlorothalonil",
                        "Azoxystrobin"
                    ]
                }
            },
            
            "potato_late_blight": {
                "name": "Potato Late Blight",
                "crop": "Potato",
                "type": "disease",
                "pathogen": "Phytophthora infestans (Oomycete)",
                "symptoms": [
                    "Water-soaked lesions on leaves",
                    "White mold on undersides",
                    "Rapid plant collapse",
                    "Tuber rot"
                ],
                "treatment": {
                    "organic": [
                        "Destroy infected plants",
                        "Copper-based fungicides"
                    ],
                    "chemical": [
                        "Metalaxyl + Mancozeb",
                        "Cymoxanil + Mancozeb"
                    ]
                }
            },
            
            "potato_healthy": {
                "name": "Healthy Potato",
                "crop": "Potato",
                "type": "healthy",
                "pathogen": "None",
                "symptoms": [
                    "Dark green healthy foliage",
                    "No lesions or spots",
                    "Vigorous growth"
                ],
                "treatment": {
                    "organic": ["Continue care"],
                    "chemical": ["No treatment needed"]
                }
            },
            
            # PEPPER DISEASES
            "pepper_bell_bacterial_spot": {
                "name": "Pepper Bell Bacterial Spot",
                "crop": "Bell Pepper",
                "type": "disease",
                "pathogen": "Xanthomonas spp. (Bacteria)",
                "symptoms": [
                    "Small raised spots on leaves",
                    "Spots may have yellow halos",
                    "Fruit lesions are raised",
                    "Defoliation in severe cases"
                ],
                "treatment": {
                    "organic": [
                        "Copper bactericides",
                        "Remove infected parts",
                        "Reduce humidity"
                    ],
                    "chemical": [
                        "Copper hydroxide",
                        "Copper + Mancozeb combinations"
                    ]
                }
            },
            
            "pepper_bell_healthy": {
                "name": "Healthy Bell Pepper",
                "crop": "Bell Pepper",
                "type": "healthy",
                "pathogen": "None",
                "symptoms": [
                    "Glossy green leaves",
                    "No spots or blemishes",
                    "Healthy fruit development"
                ],
                "treatment": {
                    "organic": ["Maintain care"],
                    "chemical": ["No treatment needed"]
                }
            }
        }
    
    def _load_pest_data(self) -> Dict:
        """Load pest information"""
        return {
            "aphids": {
                "name": "Aphids",
                "crops_affected": ["Tomato", "Pepper", "Potato", "Most crops"],
                "type": "pest",
                "description": "Small soft-bodied insects that suck plant sap",
                "identification": [
                    "Small (1-3mm) green, black, or yellow insects",
                    "Clustered on young shoots",
                    "Sticky honeydew secretion"
                ],
                "control": {
                    "organic": [
                        "Neem oil spray (5ml per liter)",
                        "Insecticidal soap",
                        "Release ladybugs"
                    ],
                    "chemical": [
                        "Imidacloprid (0.3ml per liter)",
                        "Acetamiprid (0.5g per liter)"
                    ]
                }
            }
        }
    
    def get_disease_info(self, disease_key: str) -> Optional[Dict]:
        """
        Get disease information by key
        
        Args:
            disease_key: Disease identifier key
            
        Returns:
            dict or None: Disease information
        """
        info = self.diseases.get(disease_key)
        if info:
            logger.debug(f"Found disease info for: {disease_key}")
        else:
            logger.debug(f"No disease info found for: {disease_key}")
        return info
    
    def get_pest_info(self, pest_key: str) -> Optional[Dict]:
        """Get pest information by key"""
        return self.pests.get(pest_key)
    
    def search_by_crop(self, crop: str) -> Dict:
        """Get all diseases for a specific crop"""
        crop_lower = crop.lower()
        result = {}
        
        for key, info in self.diseases.items():
            if info.get('crop', '').lower() == crop_lower:
                result[key] = info
        
        return result