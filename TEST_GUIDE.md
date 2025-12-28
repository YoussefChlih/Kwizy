# Guide de Test - Nouvelles Fonctionnalités

## [OK] Prérequis
- Serveur Flask en cours d'exécution: `python app.py`
- Accès à http://localhost:5000
- Compte utilisateur créé (optionnel mais recommandé)

## [TESTS] Tests à Effectuer

### 1. Test des Statistiques

**Sans compte (Guest):**
1. Aller sur http://localhost:5000
2. Naviguer vers "Stats"
3. [OK] Vérifier: Affichage de stats par défaut (0 quiz, 0%, niveau 1)
4. [OK] Vérifier: Pas d'erreur 404 dans la console

**Avec compte:**
1. Se connecter
2. Naviguer vers "Stats"
3. Compléter un quiz
4. Retourner aux stats
5. [OK] Vérifier: Les stats sont mises à jour
6. [OK] Vérifier: Le graphique de difficulté s'affiche

---

### 2. Test de l'Historique des Quiz

**Configuration:**
1. Se connecter à un compte
2. Naviguer vers "Stats"
3. [OK] Vérifier: Section "Historique des Quiz" visible

**Générer un historique:**
1. Aller dans "Upload" → "Générer" → "Quiz"
2. Compléter un quiz (répondre à toutes les questions)
3. Voir les résultats
4. Retourner à "Stats"
5. [OK] Vérifier: Le quiz apparaît dans l'historique
6. [OK] Vérifier: Score, date, difficulté affichés

**Détails de l'historique:**
1. Cliquer sur un quiz dans l'historique
2. [OK] Vérifier: Les détails s'affichent
3. [OK] Vérifier: Questions affichées
4. [OK] Vérifier: Réponses utilisateur vs correctes
5. [OK] Vérifier: Icônes [CORRECT] / [INCORRECT]
6. [OK] Vérifier: Explications visibles

**Actualiser:**
1. Cliquer sur "Actualiser"
2. [OK] Vérifier: Toast "Historique actualisé"
3. [OK] Vérifier: Données rechargées

---

### 3. Test du Partage de Quiz

**Générer un lien de partage:**
1. Compléter un quiz
2. Dans les résultats, cliquer sur "Partager"
3. [OK] Vérifier: Modal de partage s'ouvre
4. [OK] Vérifier: Lien généré (format: http://localhost:5000/quiz/shared/XXXXXXXX)
5. [OK] Vérifier: Message "Lien de partage généré!"

**Copier le lien:**
1. Cliquer sur "Copier"
2. [OK] Vérifier: Toast "Lien copié dans le presse-papier!"
3. Coller le lien dans un nouvel onglet (Ctrl+V dans la barre d'adresse)
4. [OK] Vérifier: Le lien fonctionne

**Tester le partage:**
1. Ouvrir le lien partagé dans un navigateur privé/incognito
2. [OK] Vérifier: Le quiz est accessible sans connexion
3. [OK] Vérifier: Les questions s'affichent correctement

---

### 4. Test de l'Export PDF

**Export sans réponses:**
1. Compléter un quiz
2. Dans les résultats, cliquer sur "Exporter PDF"
3. [OK] Vérifier: Message "Génération du PDF..."
4. [OK] Vérifier: Fichier téléchargé (quiz_XXXXX.pdf)
5. Ouvrir le PDF
6. [OK] Vérifier: Titre du quiz
7. [OK] Vérifier: Questions numérotées
8. [OK] Vérifier: Options de réponse (si QCM/Vrai-Faux)
9. [OK] Vérifier: PAS de réponses correctes affichées

**Export avec réponses:**
1. Dans les résultats, cliquer sur "PDF avec réponses"
2. [OK] Vérifier: Fichier téléchargé
3. Ouvrir le PDF
4. [OK] Vérifier: Questions + Options
5. [OK] Vérifier: Réponses correctes en vert
6. [OK] Vérifier: Explications affichées

**Vérifier la qualité du PDF:**
1. [OK] Vérifier: Mise en page propre
2. [OK] Vérifier: Texte lisible
3. [OK] Vérifier: Pas de texte coupé
4. [OK] Vérifier: Numérotation cohérente

---

### 5. Test du Design Responsive

**Desktop (> 1200px):**
1. Ouvrir en plein écran
2. [OK] Vérifier: 3-4 colonnes pour les stats
3. [OK] Vérifier: Navigation horizontale
4. [OK] Vérifier: Badges sur une ligne

**Tablette (768px - 1200px):**
1. Redimensionner la fenêtre à ~900px
2. [OK] Vérifier: 2 colonnes pour les stats
3. [OK] Vérifier: Navigation toujours horizontale
4. [OK] Vérifier: Boutons bien espacés

**Mobile (< 768px):**
1. Redimensionner à ~400px ou utiliser DevTools (F12 > Mobile)
2. [OK] Vérifier: 1 colonne pour les stats
3. [OK] Vérifier: Navigation en wrap (plusieurs lignes)
4. [OK] Vérifier: Boutons empilés verticalement
5. [OK] Vérifier: Modales adaptées
6. [OK] Vérifier: Formulaires tactiles

**Tester sur tous les écrans:**
1. Section Upload
2. [OK] Vérifier: Zone de drag&drop adaptée
3. Section Quiz
4. [OK] Vérifier: Questions lisibles
5. [OK] Vérifier: Boutons accessibles
6. Section Stats
7. [OK] Vérifier: Graphiques visibles
8. [OK] Vérifier: Historique scrollable

---

### 6. Test d'Intégration Complète

**Scénario utilisateur complet:**
1. Créer un compte
2. Se connecter
3. Upload un document PDF
4. Générer un quiz (10 questions, Moyen, QCM)
5. Répondre à toutes les questions
6. Voir les résultats
7. ✅ Vérifier: Score affiché
8. Partager le quiz
9. ✅ Vérifier: Lien généré
10. Exporter en PDF avec réponses
11. ✅ Vérifier: PDF téléchargé
12. Aller dans Stats
13. ✅ Vérifier: Historique mis à jour
14. Cliquer sur le quiz dans l'historique
15. ✅ Vérifier: Toutes les réponses visibles
16. Se déconnecter
17. Ouvrir le lien partagé
18. ✅ Vérifier: Quiz accessible publiquement

---

## [DETAILS] Problèmes Connus & Solutions

### Problème: Erreur 404 sur /api/user/guest/stats
**Solution:** Les nouvelles routes sont maintenant enregistrées. Redémarrer le serveur.

### Problème: Historique vide
**Cause:** Utilisateur non connecté ou aucun quiz complété
**Solution:** Se connecter et compléter au moins un quiz

### Problème: Export PDF échoue
**Erreur possible:** reportlab non installé
**Solution:** `pip install reportlab`

### Problème: Lien de partage ne fonctionne pas
**Cause:** Serveur pas en cours d'exécution
**Solution:** Vérifier que Flask tourne sur le port 5000

### Problème: TensorFlow prend du temps à charger
**Solution:** `USE_SENTENCE_TRANSFORMERS=false` dans .env (déjà configuré)

---

## [CHECKLIST] Checklist Finale

- [ ] Stats fonctionnent (guest + connecté)
- [ ] Historique s'affiche après quiz
- [ ] Détails d'historique affichent questions/réponses
- [ ] Partage génère un lien unique
- [ ] Lien partagé accessible sans connexion
- [ ] Export PDF sans réponses fonctionne
- [ ] Export PDF avec réponses fonctionne
- [ ] Design responsive sur mobile (< 768px)
- [ ] Design responsive sur tablette (768-1200px)
- [ ] Design responsive sur desktop (> 1200px)
- [ ] Toutes les modales s'ouvrent/ferment correctement
- [ ] Boutons de copie fonctionnent
- [ ] Toasts de notification apparaissent
- [ ] Aucune erreur console

---

## [NEXT] Prochaines Étapes Recommandées

1. **Déploiement:**
   - Configurer un serveur de production (Heroku, Render, Azure)
   - Configurer un nom de domaine
   - Les liens de partage utiliseront automatiquement le domaine

2. **Amélioration Base de Données:**
   - Créer une table `shared_quizzes` dans Supabase
   - Stocker les quiz partagés de manière persistante
   - Ajouter statistiques de vues

3. **Features Additionnelles:**
   - Partage sur réseaux sociaux
   - QR codes pour les quiz
   - Embed codes pour intégrer quiz sur d'autres sites

4. **Analytics:**
   - Tracker les vues de quiz partagés
   - Analyser les performances des utilisateurs
   - Créer des tableaux de bord admin
