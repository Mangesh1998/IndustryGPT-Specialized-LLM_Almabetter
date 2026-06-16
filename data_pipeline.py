import os
import json
import requests

# Ensure directories exist
os.makedirs("data", exist_ok=True)

# Curated NCERT History Knowledge Base (Ancient, Medieval, and Modern)
# This serves as the core verified corpus of facts from NCERT Class 6-12 History books.
ncert_raw_data = [
    # --- ANCIENT HISTORY ---
    {
        "period": "Ancient",
        "class": "Class VI / XII (Part 1)",
        "chapter": "Bricks, Beads and Bones - The Harappan Civilisation",
        "title": "Town Planning and Drainage System",
        "content": "One of the most distinctive features of Harappan cities was the carefully planned drainage system. Road and streets were laid out along an approximate grid pattern, intersecting at right angles. It seems that streets with drains were laid out first and then houses built along them. Every house was connected to the street drains. The main channels were made of bricks set in mortar and were covered with loose slabs that could be removed for cleaning. Houses had courtyard-centered layouts, with bathrooms having drains connected to the street."
    },
    {
        "period": "Ancient",
        "class": "Class VI / XII (Part 1)",
        "chapter": "Bricks, Beads and Bones - The Harappan Civilisation",
        "title": "Harappan Crafts and Trade",
        "content": "Harappans excelled in craft production, including bead-making, shell-cutting, metal-working, seal-making, and weight-making. Chanhudaro was a tiny settlement almost exclusively devoted to craft production. Beads were made from carnelian (a beautiful red stone), jasper, crystal, quartz, and steatite. Metals used included copper, bronze, gold, and silver. Harappans conducted long-distance trade, sourcing copper from Khetri in Rajasthan and Oman, gold from South India, and lapis lazuli from Shortughai in Afghanistan."
    },
    {
        "period": "Ancient",
        "class": "Class VI / XII (Part 1)",
        "chapter": "Bricks, Beads and Bones - The Harappan Civilisation",
        "title": "The Great Bath and Citadel",
        "content": "The Citadel at Mohenjodaro contains structures that were probably used for special public purposes. The Great Bath was a large rectangular tank in a courtyard surrounded by a corridor on all four sides. There were two flights of steps on the north and south leading into the tank, which was made watertight by setting bricks on edge and using a mortar of gypsum. There were rooms on three sides, in one of which was a large well. Water from the tank flowed into a huge drain. This was likely used for ritual bathing."
    },
    {
        "period": "Ancient",
        "class": "Class VI / XII (Part 1)",
        "chapter": "Kings, Farmers and Towns",
        "title": "The Sixteen Mahajanapadas",
        "content": "From the sixth century BCE, there was a growth of early states, cities, and the use of iron. The era is known for the rise of sixteen oligarchic and monarchical states known as Mahajanapadas. Among these, Magadha (in modern Bihar) became the most powerful Mahajanapada between the sixth and fourth centuries BCE. Magadha's power was attributed to agricultural productivity, rich iron mines (in modern Jharkhand) used for weapons, elephant availability in forests for the army, and strategic capitals at Rajagaha (Rajgir) and later Pataliputra (Patna)."
    },
    {
        "period": "Ancient",
        "class": "Class VI / XII (Part 1)",
        "chapter": "Kings, Farmers and Towns",
        "title": "The Mauryan Empire and Ashoka's Dhamma",
        "content": "The Mauryan Empire, founded by Chandragupta Maurya in c. 321 BCE, spanned across the subcontinent. His grandson, Ashoka, is the most famous Mauryan ruler. He conquered Kalinga but abandoned war after witnessing the bloodshed. Ashoka formulated the policy of Dhamma, which included respect towards elders, generosity towards Brahmanas and those who lacked resources, kind treatment of slaves and servants, and religious tolerance. He appointed Dhamma Mahamattas to spread these principles and inscribed them on stone pillars."
    },
    {
        "period": "Ancient",
        "class": "Class VI / XII (Part 1)",
        "chapter": "Kings, Farmers and Towns",
        "title": "Gupta Empire and Prashastis",
        "content": "By the fourth century CE, many empires, including the Gupta Empire, emerged. They depended on feudatories (samanthas) who maintained themselves through local land resources. Historical reconstruction of Gupta rule relies on coins, inscriptions, and literature, including Prashastis (eulogies written by court poets). The Prayaga Prashasti (also known as the Allahabad Pillar Inscription), composed in Sanskrit by Harishena, the court poet of Samudragupta, describes the military conquests, virtues, and divine status of the emperor."
    },
    {
        "period": "Ancient",
        "class": "Class VI / XII (Part 1)",
        "chapter": "Kinship, Caste and Class",
        "title": "Social Stratification and Dharmasutras",
        "content": "From c. 600 BCE to 600 CE, social relationships sharpened. Brahmanas compiled Sanskrit texts known as Dharmasutras and Dharmashastras to lay down norms for society. The Manusmriti, compiled between c. 200 BCE and 200 CE, is the most important of these works. These texts defined the Varna system, dividing society into four varnas: Brahmanas (priests/teachers), Kshatriyas (rulers/warriors), Vaishyas (traders/cultivators), and Shudras (servants). They also designated 'untouchables' (Chandalas) who performed polluting tasks."
    },
    {
        "period": "Ancient",
        "class": "Class VI / XII (Part 1)",
        "chapter": "Thinkers, Beliefs and Buildings",
        "title": "Teachings of Buddhism",
        "content": "Buddhism grew rapidly under the influence of Siddhartha Gautama (the Buddha). According to Buddhist teachings, the world is transient (anicca) and constantly changing; it is also soulless (anatta) as there is nothing permanent. Within this transient world, sorrow (dukkha) is intrinsic to human existence. By following the Middle Path between severe penance and self-indulgence, humans can rise above these worldly troubles. The Buddha emphasized individual agency and righteous action as the means to escape the cycle of rebirth and attain Nibbana."
    },
    {
        "period": "Ancient",
        "class": "Class VI / XII (Part 1)",
        "chapter": "Thinkers, Beliefs and Buildings",
        "title": "The Sanchi Stupa",
        "content": "Stupas were sacred mounds containing relics of the Buddha, such as his bodily remains or objects he used. Sanchi Stupa in Madhya Pradesh is one of the best-preserved Buddhist monuments. In the 19th century, Europeans (like the French and British) wanted to take away the eastern gateway to display in museums. However, the rulers of Bhopal, Shahjehan Begum and Sultan Jehan Begum, provided funding to preserve the monument in situ, building a museum and guesthouse, making it a landmark of ancient Indian art."
    },
    # --- MEDIEVAL HISTORY ---
    {
        "period": "Medieval",
        "class": "Class VII / XII (Part 2)",
        "chapter": "The Delhi Sultans",
        "title": "Administration and Consolidated Rule",
        "content": "The Delhi Sultanate consolidated its rule in northern India starting in the 13th century. Rulers like Iltutmish, Alauddin Khalji, and Muhammad bin Tughluq centralized administration. They appointed military commanders as governors of territories of varying sizes, called iqtas, and their holders were known as iqtadars or muqtis. The duty of the muqtis was to lead military campaigns and maintain law and order in their iqtas, in exchange for which they collected the revenues of their assignments as salary."
    },
    {
        "period": "Medieval",
        "class": "Class VII / XII (Part 2)",
        "chapter": "The Delhi Sultans",
        "title": "Alauddin Khalji's Market Control reforms",
        "content": "Alauddin Khalji (r. 1296–1316) introduced strict administrative and market reforms to maintain a large standing army against Mongol invasions. He fixed the prices of essential commodities like food grains, sugar, cooking oil, and cloth. Merchants had to register with the state, and any hoarding or short-weight selling was severely punished. The market superintendent (Shahna-i-Mandi) monitored the markets daily. Alauddin also reformed land revenue, measuring land and collecting tax directly in cash."
    },
    {
        "period": "Medieval",
        "class": "Class VII / XII (Part 2)",
        "chapter": "The Mughal Empire",
        "title": "Mansabdari System",
        "content": "The Mughals organized their administration around the Mansabdari system. The term mansabdar refers to an individual who holds a mansab, meaning a position or rank. It was a grading system used to fix rank, salary, and military responsibilities. Rank and salary were determined by a numerical value called 'zat'. The higher the zat, the more prestigious the noble's position and the larger his salary. Mansabdars had to maintain a specified number of cavalrymen (sawar), present them for review, and register them."
    },
    {
        "period": "Medieval",
        "class": "Class VII / XII (Part 2)",
        "chapter": "The Mughal Empire",
        "title": "Land Revenue and the Zabt System",
        "content": "The main source of income for the Mughal Empire was tax on agricultural produce. Akbar's revenue minister, Todar Mal, carried out a careful survey of crop yields, prices, and areas cultivated for a 10-year period (1570–1580). On the basis of this data, tax was fixed on each crop in cash. Each province was divided into revenue circles with its own schedule of revenue rates for individual crops. This system of revenue administration was known as Zabt, and it was prevalent in areas where Mughal administrators could measure land."
    },
    {
        "period": "Medieval",
        "class": "Class VII / XII (Part 2)",
        "chapter": "An Imperial Capital - Vijayanagara",
        "title": "Founding and Royal Center of Vijayanagara",
        "content": "The Vijayanagara Empire was founded in 1336 by two brothers, Harihara and Bukka. The empire stretched from the Krishna river to the extreme south. The capital city, Vijayanagara (modern Hampi), was situated in the natural basin formed by the Tungabhadra river. The city was surrounded by seven lines of massive stone fortification walls, which enclosed not only the city but also agricultural fields and forests. The Mahanavami Dibba was a massive platform where the king performed elaborate rituals during the Navaratri festival."
    },
    {
        "period": "Medieval",
        "class": "Class VII / XII (Part 2)",
        "chapter": "An Imperial Capital - Vijayanagara",
        "title": "Krishna Deva Raya and Hampi Temples",
        "content": "Krishna Deva Raya (r. 1509–1529) was the most prominent ruler of the Tuluva dynasty of Vijayanagara. He expanded the empire and patronized art and literature. He built the famous Virupaksha Temple's majestic eastern gopuram and the Vitthala Temple complex, famous for its musical pillars and stone chariot. He also established a suburban township near Vijayanagara called Nagalapuram, named after his mother. Vijayanagara kings used the title 'Hindu Suratrana' (Sultan among Hindu kings)."
    },
    {
        "period": "Medieval",
        "class": "Class VII / XII (Part 2)",
        "chapter": "Bhakti-Sufi Traditions",
        "title": "Sufism and Chishti Silsila",
        "content": "Sufism was a mystical movement within Islam that rejected dogmatism and emphasized love, devotion, and compassion for humanity as paths to God. Sufis organized themselves into orders or silsilas, named after their founders or places of origin. The Chishti silsila, established in India by Khwaja Muinuddin Chishti in the late 12th century, was the most influential. Chishtis adapted to local environments, adopting musical gatherings (Sama) and congregational living in hospices (Khanqahs) run by Sheikhs."
    },
    {
        "period": "Medieval",
        "class": "Class VII / XII (Part 2)",
        "chapter": "Bhakti-Sufi Traditions",
        "title": "Kabir and Nirguna Bhakti",
        "content": "Kabir (c. 14th-15th century) is one of the most prominent Bhakti poets. He belonged to a family of weavers near Varanasi. Kabir's teachings rejected major religious traditions, rituals, and caste hierarchies. He advocated Nirguna Bhakti—devotion to a formless, supreme reality, whom he addressed as Allah, Ram, Hazrat, or Hari. His verses, composed in a regional language (Sadhukkarri Bhasha), are preserved in three collections: Kabir Bijak (preserved in Kabirpanthi tradition in Bihar/UP), Kabir Granthavali (Rajasthan), and the Adi Granth Sahib."
    },
    # --- MODERN HISTORY ---
    {
        "period": "Modern",
        "class": "Class VIII / XII (Part 3)",
        "chapter": "From Trade to Territory",
        "title": "Battle of Plassey (1757)",
        "content": "The Battle of Plassey was fought on June 23, 1757, between Siraj-ud-Daulah, the Nawab of Bengal, and the British East India Company led by Robert Clive. The conflict arose due to the Nawab's opposition to the Company's fortifying Calcutta and abusing trade privileges. Clive won the battle by bribing Mir Jafar, Siraj-ud-Daulah's commander-in-chief, promising to make him Nawab. Siraj-ud-Daulah was defeated and executed. This victory established British political hegemony in Bengal and India."
    },
    {
        "period": "Modern",
        "class": "Class VIII / XII (Part 3)",
        "chapter": "From Trade to Territory",
        "title": "Battle of Buxar (1764) and Diwani Rights",
        "content": "After Mir Jafar's successor, Mir Qasim, fell out with the British, the Battle of Buxar was fought on October 22, 1764. The joint forces of Mir Qasim, Shuja-ud-Daulah (Nawab of Awadh), and Shah Alam II (Mughal Emperor) were defeated by Major Hector Munro. This led to the Treaty of Allahabad in 1765, by which the Mughal Emperor granted the Diwani rights (the right to collect land revenue) of Bengal, Bihar, and Orissa to the East India Company, turning it into a sovereign ruler."
    },
    {
        "period": "Modern",
        "class": "Class VIII / XII (Part 3)",
        "chapter": "From Trade to Territory",
        "title": "Subsidiary Alliance and Doctrine of Lapse",
        "content": "The East India Company used aggressive administrative policies to annex Indian states. Richard Wellesley introduced the Subsidiary Alliance system, under which rulers had to accept a British resident at court, dismantle their army, and pay for the maintenance of a British subsidiary force. If they failed, part of their territory was annexed (e.g. Awadh in 1801). Lord Dalhousie introduced the Doctrine of Lapse, which decreed that if an Indian ruler died without a male heir, his kingdom would 'lapse' and become part of British territory (e.g., Satara, Sambalpur, Jhansi)."
    },
    {
        "period": "Modern",
        "class": "Class VIII / XII (Part 3)",
        "chapter": "Ruling the Countryside",
        "title": "Land Revenue Systems - Permanent Settlement",
        "content": "To secure regular revenue, the British introduced three land systems. Lord Cornwallis introduced the Permanent Settlement in Bengal in 1793. The rajas and taluqdars were recognized as Zamindars. They were asked to collect rent from peasants and pay a fixed revenue to the Company. The amount to be paid was fixed permanently. This led to high exploitation of peasants, who often lost their lands to moneylenders when crops failed, while zamindars lost their estates if they failed to pay the fixed sum."
    },
    {
        "period": "Modern",
        "class": "Class VIII / XII (Part 3)",
        "chapter": "Ruling the Countryside",
        "title": "Mahalwari and Ryotwari Land Revenue Systems",
        "content": "In the North-West Provinces, Holt Mackenzie devised the Mahalwari Settlement in 1822, where revenue was collected from the village or group of villages called 'mahal' and revised periodically. In the Deccan and South India, Thomas Munro introduced the Ryotwari Settlement. Since there were no traditional zamindars, the settlement was made directly with the cultivators (ryots) who had cleared the land. Cultivated fields were surveyed before revenue assessment, which was kept high, leading to peasant migrations."
    },
    {
        "period": "Modern",
        "class": "Class VIII / XII (Part 3)",
        "chapter": "When People Rebel - 1857 and After",
        "title": "Outbreak and Causes of the Revolt of 1857",
        "content": "The Revolt of 1857 (First War of Independence) was a massive armed rebellion against East India Company rule. It began on May 10, 1857, with a mutiny of sepoys in Meerut. The immediate cause was the introduction of the Enfield Rifle, whose cartridges were rumored to be greased with cow and pig fat, offending both Hindu and Muslim sepoys. Deeper causes included the annexation policies (like Awadh), high taxation, land confiscation, destruction of local handicraft industries, and fear of forced religious conversion."
    },
    {
        "period": "Modern",
        "class": "Class VIII / XII (Part 3)",
        "chapter": "When People Rebel - 1857 and After",
        "title": "Centers and Leaders of the 1857 Revolt",
        "content": "The revolt spread rapidly across North and Central India. The sepoys marched to Delhi and declared the aging Mughal Emperor Bahadur Shah Zafar as their leader. Key centers of the revolt and their leaders included: Kanpur led by Nana Sahib (adopted son of Peshwa Baji Rao II) and Tantia Tope; Lucknow led by Begum Hazrat Mahal and Birjis Qadr; Jhansi led by Rani Lakshmibai, who fought valiantly; and Bihar led by Kunwar Singh, an elderly zamindar of Jagdishpur."
    },
    {
        "period": "Modern",
        "class": "Class VIII / XII (Part 3)",
        "chapter": "Nationalist Movement",
        "title": "Partition of Bengal and Swadeshi Movement (1905)",
        "content": "In 1905, Viceroy Lord Curzon partitioned Bengal, claiming it was for administrative convenience, but the real motive was to split the center of Indian nationalism and create a Hindu-Muslim divide. This sparked the Swadeshi and Boycott Movement. Moderates and Extremists (led by Lal-Bal-Pal: Lala Lajpat Rai, Bal Gangadhar Tilak, and Bipin Chandra Pal) united. Tilak raised the slogan: 'Swaraj is my birthright and I shall have it!' People boycotted British goods and promoted local Swadeshi industries, national schools, and vernacular literature."
    },
    {
        "period": "Modern",
        "class": "Class VIII / XII (Part 3)",
        "chapter": "Nationalist Movement",
        "title": "Non-Cooperation Movement (1920-1922)",
        "content": "Mahatma Gandhi launched the Non-Cooperation Movement in 1920 in response to the Rowlatt Act, the Jallianwala Bagh Massacre (1919), and to support the Khilafat Movement. Gandhi urged Indians to surrender government titles, boycott schools, courts, and foreign clothes, and adopt Khadi. The movement saw massive public participation. However, in February 1922, a violent clash occurred at Chauri Chaura in Gorakhpur, where a crowd set fire to a police station, killing 22 policemen. Gandhi, advocating absolute non-violence (Ahimsa), immediately suspended the movement."
    },
    {
        "period": "Modern",
        "class": "Class VIII / XII (Part 3)",
        "chapter": "Nationalist Movement",
        "title": "Dandi Salt March and Civil Disobedience (1930)",
        "content": "In 1930, Mahatma Gandhi declared that he would lead a march to break the salt law, which gave the state a monopoly on manufacture and sale of salt, taxing a basic necessity. Gandhi and 78 followers marched 240 miles from Sabarmati Ashram to the coastal town of Dandi in Gujarat. On April 6, 1930, he broke the law by picking up natural salt from the shore. This marked the launch of the Civil Disobedience Movement, which involved illegal salt manufacture, boycott of foreign cloth, picketing of liquor shops, and refusal to pay revenue taxes."
    },
    {
        "period": "Modern",
        "class": "Class VIII / XII (Part 3)",
        "chapter": "Nationalist Movement",
        "title": "Quit India Movement (1942)",
        "content": "Amidst the crisis of World War II and the failure of the Cripps Mission, Mahatma Gandhi launched the Quit India Movement in August 1942. At the All India Congress Committee meeting in Bombay, Gandhi delivered the historic 'Do or Die' (Karo ya Maro) speech. The British responded by immediately arresting Gandhi and almost all top Congress leaders. This triggered a leaderless, spontaneous mass rebellion across the country, characterized by strikes, attacks on railway lines, telegraph wires, and government buildings, which the British suppressed with brute force."
    }
]

# Generate QA Pairs for Fine-Tuning
# These are mapped directly to the NCERT content above.
qa_pairs = [
    {
        "instruction": "Explain the features of the town planning and drainage system in the Harappan Civilisation.",
        "input": "",
        "output": "The Harappan cities were characterised by carefully planned grid-pattern roads and streets that intersected at right angles. The streets with drains were laid out first, followed by the houses. Every house was connected directly to the street drains, which were covered with loose brick slabs that could be removed for cleaning. Houses featured courtyard-centered layouts, and bathrooms had drains running directly into the street."
    },
    {
        "instruction": "What were the main craft activities in the Harappan Civilisation and where did they source materials from?",
        "input": "",
        "output": "Craft activities in the Harappan Civilisation included bead-making, shell-cutting, metal-working, seal-making, and weight-making. Chanhudaro was a prominent settlement dedicated exclusively to crafts. Beads were crafted from stones like carnelian, jasper, crystal, quartz, and steatite, and metals like copper, bronze, gold, and silver. For raw materials, Harappans traded long distances: copper was sourced from Khetri in Rajasthan and Oman, gold from South India, and lapis lazuli from Shortughai in Afghanistan."
    },
    {
        "instruction": "Describe the features and purpose of the Great Bath in Mohenjodaro.",
        "input": "",
        "output": "The Great Bath was a large rectangular tank situated in the Citadel of Mohenjodaro, surrounded by corridors on all four sides. It was made watertight using bricks set on edge with a gypsum mortar. Steps led into the tank from the north and south, and it was surrounded by rooms, one of which housed a large well. Water was drained out of the tank via a massive brick channel. The Great Bath was likely used for special ritual bathing."
    },
    {
        "instruction": "Why did Magadha become the most powerful Mahajanapada between the 6th and 4th centuries BCE?",
        "input": "",
        "output": "Magadha's rise to power was driven by multiple factors: 1. Exceptional agricultural productivity in the region. 2. Rich iron ore mines (in modern Jharkhand) that provided materials for strong weapons and tools. 3. Forests containing elephants, which were captured and trained for the army. 4. Strategic capitals at Rajagaha (Rajgir), which was fortified, and later Pataliputra (Patna) situated along the Ganga river route."
    },
    {
        "instruction": "What was Ashoka's policy of Dhamma?",
        "input": "",
        "output": "Formulated by Emperor Ashoka of the Mauryan Empire, Dhamma was a set of ethical principles to promote social harmony. It advocated: respect towards elders; generosity towards Brahmanas, ascetics, and the poor; kind treatment of slaves and servants; and religious tolerance. Ashoka inscribed these principles on stone pillars throughout his empire and appointed special officers called 'Dhamma Mahamattas' to propagate them."
    },
    {
        "instruction": "How do historians reconstruct the history of the Gupta Empire? Explain with reference to Prashastis.",
        "input": "",
        "output": "Historians reconstruct Gupta history using coins, inscriptions, texts, and Prashastis (court eulogies written in praise of kings). A key example is the Prayaga Prashasti (Allahabad Pillar Inscription), composed in Sanskrit by Harishena, the court poet of Emperor Samudragupta. This text outlines the king's military conquests, exceptional virtues, intelligence, and describes him as equal to deities, providing rich details about the administrative and political structure."
    },
    {
        "instruction": "What was the Varna system according to Brahmanical texts like Manusmriti?",
        "input": "",
        "output": "The Varna system divided society into four hierarchical groups with defined duties: 1. Brahmanas (priests and teachers, who studied/taught Vedas). 2. Kshatriyas (rulers and warriors, who protected people). 3. Vaishyas (cultivators, herders, and traders). 4. Shudras (assigned to serve the three higher varnas). Brahmanical texts like the Manusmriti (compiled c. 200 BCE - 200 CE) enforced these rules and also designated 'untouchables' (Chandalas) to perform polluting tasks like handling corpses."
    },
    {
        "instruction": "What are the core teachings of Buddhism regarding the nature of the world?",
        "input": "",
        "output": "According to the Buddha's teachings: 1. The world is transient (anicca) and constantly changing. 2. The world is soulless (anatta), meaning there is nothing permanent or eternal. 3. Sorrow (dukkha) is intrinsic to human existence. 4. Humans can overcome sorrow by following the 'Middle Path' (avoiding extreme penance and self-indulgence) and practicing righteous action (karma) to break the cycle of rebirth and attain Nibbana."
    },
    {
        "instruction": "How was the Sanchi Stupa preserved in the 19th century and who funded it?",
        "input": "",
        "output": "In the 19th century, Sanchi Stupa was preserved in situ through the efforts and funding of the Begums of Bhopal (Shahjehan Begum and her successor Sultan Jehan Begum). While Europeans wanted to take the eastern gateway to display in museums in Paris or London, the rulers provided financial support to make plaster-of-paris copies for them, built a museum and a guesthouse at the site, and funded archaeological research, preventing the monument from being looted."
    },
    {
        "instruction": "Explain the Iqta system under the Delhi Sultanate.",
        "input": "",
        "output": "The Iqta system was an administrative system where the Delhi Sultans (such as Iltutmish and Alauddin Khalji) divided their empire into territories called 'iqtas' and assigned them to military commanders. These commanders, known as iqtadars or muqtis, were responsible for leading military campaigns, maintaining law and order in their assigned regions, and collecting land revenue. From the revenue collected, they paid their soldiers and drew their own salaries."
    },
    {
        "instruction": "Describe the market and price control reforms introduced by Alauddin Khalji.",
        "input": "",
        "output": "To maintain a large standing army, Alauddin Khalji fixed the prices of essential commodities like food grains, oil, sugar, and cloth in Delhi. Merchants had to register with the state, and hoarding or selling below weight was severely punished. The market superintendent (Shahna-i-Mandi) monitored transactions daily. He also reformed the land revenue system by introducing land measurement and collecting tax directly in cash, bypassing local chieftains."
    },
    {
        "instruction": "Explain the Mansabdari system of the Mughal Empire.",
        "input": "",
        "output": "The Mansabdari system was a grading system used by the Mughals to determine the rank, salary, and military responsibilities of nobles. Each noble held a 'mansab' (rank). Rank and salary were fixed by a numerical value called 'zat' (higher zat meant higher prestige and pay). The mansabdar was required to maintain a specific number of cavalrymen (sawar), bring them for registration and branding, and present them for military review."
    },
    {
        "instruction": "What was the Zabt system in the Mughal Empire?",
        "input": "",
        "output": "The Zabt system was a land revenue administration system introduced during Akbar's reign by his revenue minister, Raja Todar Mal. It was based on a careful 10-year survey (1570–1580) of crop yields, prices, and cultivated areas. Tax was calculated on each crop and collected in cash. Provinces were divided into revenue circles with specific rates. This system was used in central parts of the empire where land could be measured and surveyed."
    },
    {
        "instruction": "Describe the fortifications and features of the Vijayanagara Empire's capital.",
        "input": "",
        "output": "The capital city, Vijayanagara (Hampi), was situated in the Tungabhadra river basin. It was famous for being enclosed by seven lines of massive stone fortification walls. Uniquely, these walls enclosed not only the urban center but also agricultural fields, gardens, and forests, ensuring food supply during sieges. It featured a Royal Center containing the Mahanavami Dibba, a massive platform used by kings for rituals and festival performances."
    },
    {
        "instruction": "Who was Krishna Deva Raya? What were his contributions to the Vijayanagara Empire?",
        "input": "",
        "output": "Krishna Deva Raya (r. 1509–1529) was the most famous ruler of the Vijayanagara Empire, belonging to the Tuluva dynasty. He consolidated and expanded the empire, built the majestic eastern gopuram of the Virupaksha Temple, and built the Vitthala Temple complex with its musical pillars and stone chariot. He also wrote literature, established the town of Nagalapuram, and adopted the title 'Hindu Suratrana' (Sultan among Hindu kings)."
    },
    {
        "instruction": "What were the main characteristics of Sufism and the Chishti order in India?",
        "input": "",
        "output": "Sufism was a mystical Islamic movement focused on love, devotion, and compassion as paths to God, rejecting rigid rituals. Sufis organized into orders (silsilas). The Chishti silsila, founded in India by Khwaja Muinuddin Chishti in the 12th century, became highly popular. They integrated local practices, held musical gatherings (Sama) to induce spiritual ecstasy, and lived in communal hospices (Khanqahs) open to all classes and religions."
    },
    {
        "instruction": "Describe the teachings of Kabir and the collections in which his verses are preserved.",
        "input": "",
        "output": "Kabir (14th-15th century) rejected orthodox religious rituals, caste distinctions, and idol worship. He preached Nirguna Bhakti, devotion to a formless supreme god whom he called Allah, Ram, or Hari, using everyday regional language. His verses are preserved in three major collections: the Kabir Bijak (in Bihar/UP), the Kabir Granthavali (in Rajasthan), and the Adi Granth Sahib (the holy scripture of Sikhism)."
    },
    {
        "instruction": "How did Robert Clive win the Battle of Plassey in 1757?",
        "input": "",
        "output": "Robert Clive, representing the British East India Company, defeated Nawab Siraj-ud-Daulah of Bengal at the Battle of Plassey in 1757. Clive won by conspiring with Mir Jafar, the Nawab's commander-in-chief. Clive promised to make Mir Jafar the Nawab of Bengal in exchange for his non-participation. During the battle, Mir Jafar held back his forces, leading to Siraj-ud-Daulah's defeat and subsequent execution, establishing British control."
    },
    {
        "instruction": "Explain the significance of the Battle of Buxar (1764) and the Treaty of Allahabad.",
        "input": "",
        "output": "The Battle of Buxar (1764) was fought between the British and the joint forces of Mir Qasim, Shuja-ud-Daulah (Awadh), and Mughal Emperor Shah Alam II. The British victory resulted in the Treaty of Allahabad (1765), under which the Mughal Emperor granted the Diwani rights (revenue collection rights) of Bengal, Bihar, and Orissa to the East India Company. This transformed the Company from a trading body into a territorial ruler with massive financial resources."
    },
    {
        "instruction": "Compare the Subsidiary Alliance and the Doctrine of Lapse.",
        "input": "",
        "output": "Both were British annexation policies. Under the Subsidiary Alliance (introduced by Lord Wellesley), an Indian ruler had to disband his army, accept a British resident, and pay for British troops; failure led to territory annexation. Under the Doctrine of Lapse (introduced by Lord Dalhousie), if an Indian ruler died without a direct male heir, his kingdom was annexed and became part of British territory (e.g. Jhansi, Satara, Sambalpur)."
    },
    {
        "instruction": "Describe the Permanent Settlement land revenue system of 1793.",
        "input": "",
        "output": "Introduced by Lord Cornwallis in Bengal in 1793, the Permanent Settlement fixed the land revenue permanently. Local rajas and taluqdars were recognized as Zamindars, responsible for collecting rent from peasants and paying a fixed share to the Company. Because the revenue was fixed extremely high, zamindars heavily exploited the peasants. Zamindars who failed to pay on time had their estates auctioned off by the British."
    },
    {
        "instruction": "How did the Mahalwari and Ryotwari systems differ from the Permanent Settlement?",
        "input": "",
        "output": "Unlike the Permanent Settlement (where revenue was fixed permanently with Zamindars), the Mahalwari system (1822) assessed revenue on the entire village ('mahal') collectively and was revised periodically. The Ryotwari system (introduced by Thomas Munro in Southern India) bypassed Zamindars entirely, making revenue settlements directly with the cultivators ('ryots') based on detailed surveys of their fields, with rates revised periodically."
    },
    {
        "instruction": "What were the immediate and deep-seated causes of the Revolt of 1857?",
        "input": "",
        "output": "The immediate cause of the Revolt of 1857 was the introduction of the Enfield Rifle, whose grease cartridges sepoys had to bite open; rumors spread they were greased with cow and pig fat, offending Hindu and Muslim sepoys. Deep-seated causes included Dalhousie's annexation policies (Doctrine of Lapse), the annexation of Awadh, high land revenue taxes that ruined peasants, the decline of local artisans due to British imports, and fears of forced Christian conversion."
    },
    {
        "instruction": "Name the key leaders and centers of the Revolt of 1857.",
        "input": "",
        "output": "Key centers and leaders of the Revolt of 1857 included: Delhi, where sepoys proclaimed the Mughal Emperor Bahadur Shah Zafar as their symbol; Kanpur, led by Nana Sahib and Tantia Tope; Lucknow, led by Begum Hazrat Mahal and her son Birjis Qadr; Jhansi, led by Rani Lakshmibai, who fought on the battlefield; and Bihar (Jagdishpur), led by the elderly zamindar Kunwar Singh."
    },
    {
        "instruction": "What was the Swadeshi Movement and what triggered it?",
        "input": "",
        "output": "The Swadeshi Movement (1905) was triggered by Viceroy Lord Curzon's partition of Bengal, which aimed to divide the center of Indian nationalism. The movement was led by leaders like Lal-Bal-Pal. It promoted self-reliance (Swadeshi) by boycotting foreign British goods, burning foreign cloth, and promoting indigenous schools, vernacular literature, and local enterprises like swadeshi textile mills."
    },
    {
        "instruction": "Explain the causes and suspension of the Non-Cooperation Movement.",
        "input": "",
        "output": "Launched by Mahatma Gandhi in 1920, the Non-Cooperation Movement protested the Rowlatt Act, the Jallianwala Bagh Massacre, and supported the Khilafat cause. It urged boycotting government institutions, foreign cloth, and titles. In February 1922, a protest turned violent in Chauri Chaura, Gorakhpur, where a crowd burned down a police station, killing 22 officers. Adhering strictly to non-violence (Ahimsa), Gandhi suspended the movement immediately."
    },
    {
        "instruction": "What was the Salt Satyagraha of 1930?",
        "input": "",
        "output": "The Salt Satyagraha was a protest led by Mahatma Gandhi against the British salt monopoly and salt tax. In March 1930, Gandhi and 78 followers marched 240 miles from Sabarmati Ashram to Dandi, Gujarat. On April 6, 1930, Gandhi manufactured salt by picking it up from the beach, breaking the law. This action launched the nation-wide Civil Disobedience Movement, which involved boycotts and non-payment of taxes."
    },
    {
        "instruction": "Describe the Quit India Movement of 1942.",
        "input": "",
        "output": "Launched by Mahatma Gandhi in August 1942 during World War II, the Quit India Movement demanded an immediate British withdrawal from India. Gandhi gave the call 'Do or Die' (Karo ya Maro). Although Gandhi and top leaders were arrested immediately, a massive, leaderless countrywide rebellion broke out. It featured strikes, sabotage of railway lines and communication wires, and clashes with police, which the British suppressed violently."
    }
]

# Fetch extra from Hugging Face if available
try:
    print("Attempting to load extra history data from Hugging Face...")
    from datasets import load_dataset
    ds = load_dataset("Bhargavtz/Indian_history_QA", split="train", timeout=10)
    print("HF Dataset loaded successfully!")
    
    extra_count = 0
    for row in ds:
        q = row.get("question", "") or row.get("instruction", "")
        a = row.get("answer", "") or row.get("output", "")
        if q and a and len(q) > 10 and len(a) > 10:
            qa_pairs.append({
                "instruction": q,
                "input": "",
                "output": a
            })
            extra_count += 1
            # Add to corpus too
            ncert_raw_data.append({
                "period": "Indian History",
                "class": "HuggingFace QA Source",
                "chapter": "General Q&A",
                "title": q[:50] + "...",
                "content": a
            })
            if extra_count >= 150: # Cap extra elements
                break
    print(f"Added {extra_count} additional QA pairs from Hugging Face.")
except Exception as e:
    print(f"Could not load extra Hugging Face dataset (Reason: {e}). Using core NCERT dataset.")

# Write data/ncert_corpus.json
corpus_filepath = os.path.join("data", "ncert_corpus.json")
with open(corpus_filepath, "w", encoding="utf-8") as f:
    json.dump(ncert_raw_data, f, indent=4, ensure_ascii=False)

# Write data/ncert_qa_dataset.json
qa_filepath = os.path.join("data", "ncert_qa_dataset.json")
with open(qa_filepath, "w", encoding="utf-8") as f:
    json.dump(qa_pairs, f, indent=4, ensure_ascii=False)

print("\n--- Pipeline Completed Successfully! ---")
print(f"Corpus Saved: {corpus_filepath} ({len(ncert_raw_data)} text blocks)")
print(f"QA Dataset Saved: {qa_filepath} ({len(qa_pairs)} question-answer pairs)")
