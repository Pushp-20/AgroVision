# General educational guidance; not a substitute for local agricultural diagnosis.
DISEASE_INFO = {
    'Bacterial spot': {
        'cause': 'Bacterial pathogens, commonly Xanthomonas species.',
        'symptoms': 'Small dark water-soaked spots that may become brown or black; leaf yellowing and lesions on fruit can occur.',
        'precautions': 'Use clean planting material, avoid working with wet plants, limit overhead irrigation, and remove heavily infected debris according to local guidance.'
    },
    'Early blight': {
        'cause': 'Fungal pathogens, commonly Alternaria species.',
        'symptoms': 'Brown leaf lesions, often with concentric rings, usually starting on older leaves.',
        'precautions': 'Improve airflow, mulch to reduce soil splash, remove infected debris, and consult local guidance for appropriate control.'
    },
    'Late blight': {
        'cause': 'Phytophthora infestans, an oomycete (water mold).',
        'symptoms': 'Rapidly expanding dark, water-soaked lesions; whitish growth may appear under humid conditions.',
        'precautions': 'Act promptly: isolate suspicious plants where feasible, avoid wetting foliage, and contact local agricultural extension services.'
    },
    'Leaf mold': {
        'cause': 'Passalora fulva (also called Fulvia fulva), a fungal pathogen.',
        'symptoms': 'Yellow patches on upper leaf surfaces with olive-green or grayish mold beneath.',
        'precautions': 'Reduce humidity, increase ventilation, space plants adequately, and remove affected foliage carefully.'
    },
    'Septoria leaf spot': {
        'cause': 'Septoria lycopersici, a fungal pathogen.',
        'symptoms': 'Numerous small circular spots with pale centers and darker borders, often on lower leaves.',
        'precautions': 'Avoid overhead watering, improve airflow, mulch, and remove infected plant debris.'
    },
    'Spider mites Two spotted spider mite': {
        'cause': 'Feeding damage from two-spotted spider mites (Tetranychus urticae).',
        'symptoms': 'Fine yellow stippling, bronzing, and sometimes delicate webbing on leaves.',
        'precautions': 'Inspect leaf undersides, reduce plant stress, and seek locally appropriate integrated pest-management advice.'
    },
    'Target spot': {
        'cause': 'Usually Corynespora cassiicola, a fungal pathogen.',
        'symptoms': 'Brown lesions that may develop concentric rings; leaves may yellow and drop.',
        'precautions': 'Improve ventilation, avoid prolonged leaf wetness, and manage infected plant debris.'
    },
    'Tomato mosaic virus': {
        'cause': 'Tomato mosaic virus (ToMV).',
        'symptoms': 'Mottled light and dark green leaves, distortion, and sometimes reduced growth.',
        'precautions': 'Sanitize tools and hands, avoid handling healthy plants after infected ones, and use clean seed or transplants.'
    },
    'Tomato YellowLeaf Curl Virus': {
        'cause': 'Tomato yellow leaf curl virus (TYLCV), typically spread by whiteflies.',
        'symptoms': 'Upward curling, yellowing, smaller leaves, and stunted plant growth.',
        'precautions': 'Monitor whiteflies, remove infected plants according to local guidance, and use resistant varieties where available.'
    },
    'healthy': {
        'cause': 'No disease identified by the model in this image.',
        'symptoms': 'No recognized disease pattern detected; this does not guarantee the plant is disease-free.',
        'precautions': 'Continue regular monitoring, appropriate watering, sanitation, and balanced nutrition.'
    },
}

def readable_name(class_name):
    name = class_name.replace('Tomato_', '').replace('Tomato___', '').replace('_', ' ').strip()
    return ' '.join(name.split())

def get_disease_info(class_name):
    name = readable_name(class_name)
    return DISEASE_INFO.get(name, {
        'cause': 'Specific cause not available in the local information library.',
        'symptoms': 'Inspect the plant and seek confirmation from an agricultural specialist.',
        'precautions': 'Avoid unnecessary chemical treatments until the condition is confirmed.'
    })
