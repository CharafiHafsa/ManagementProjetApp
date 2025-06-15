select * from base_de_donnee_project;

INSERT INTO base_de_donnee_groupe (id, nom_groupe, nbr_membre, projet_id)
VALUES (2, 'Groupe A', 2, 6);
INSERT INTO base_de_donnee_groupe (id, nom_groupe, nbr_membre, projet_id)
VALUES (3, 'Groupe B', 2, 6);
INSERT INTO base_de_donnee_groupe (id, nom_groupe, nbr_membre, projet_id)
VALUES (4, 'Groupe C', 2, 6);
INSERT INTO base_de_donnee_groupe (id, nom_groupe, nbr_membre, projet_id)
VALUES (5, 'Groupe D', 2, 6);
INSERT INTO base_de_donnee_etudiant 
(id, filiere, photo_profil, departement, email_etudiant, password, nom, prenom, last_login, is_verified)
VALUES
(2, 'Informatique', 'images/profile.jpeg', 'Sciences', 'etudiant1@example.com', 'hashedpassword1', 'Ali', 'Ben', NULL, TRUE),
(3, 'Cybersecurity', 'images/profile.jpeg', 'Maths', 'etudiant2@example.com', 'hashedpassword2', 'Sana', 'Khan', NULL, TRUE),
(4, 'Informatique', 'images/profile.jpeg', 'Sciences', 'etudiant3@example.com', 'hashedpassword1', 'bella', 'lina', NULL, TRUE),
(5, 'Informatique', 'images/profile.jpeg', 'Sciences', 'etudiant4@example.com', 'hashedpassword1', 'kjsd', 'uye', NULL, TRUE),
(6, 'Informatique', 'images/profile.jpeg', 'Sciences', 'etudiant5@example.com', 'hashedpassword1', 'soud', 'oth', NULL, TRUE),
(7, 'Informatique', 'images/profile.jpeg', 'Sciences', 'etudiant6@example.com', 'hashedpassword1', 'nifo', 'bt', NULL, TRUE),
(8, 'Informatique', 'images/profile.jpeg', 'Sciences', 'etudiant7@example.com', 'hashedpassword1', 'wei', 'qw', NULL, TRUE),
(9, 'Informatique', 'images/profile.jpeg', 'Sciences', 'etudiant8@example.com', 'hashedpassword1', 'few', 'bf', NULL, TRUE),
(10, 'Informatique', 'images/profile.jpeg', 'Sciences', 'etudiant9@example.com', 'hashedpassword1', 'pqma', 'qwe', NULL, TRUE),
(11, 'Informatique', 'images/profile.jpeg', 'Sciences', 'etudiant110@example.com', 'hashedpassword1', 'wsf', 'tre', NULL, TRUE),
(12, 'Informatique', 'images/profile.jpeg', 'Sciences', 'etudiant123@example.com', 'hashedpassword1', 'wer', 'qqw', NULL, TRUE);


INSERT INTO base_de_donnee_etudiant_groupes (etudiant_id, groupe_id)
VALUES 
(2, 2),
(3, 2),
(4, 3),
(5, 3),
(6, 4),
(7, 4),
(8, 5),
(9, 5);
select * from base_de_donnee_etudiant;

select * from base_de_donnee_groupe;

select * from base_de_donnee_taches;


INSERT INTO base_de_donnee_etudiant_groupes (etudiant_id, groupe_id)
VALUES 
(10, 2),
(11, 2),
(12,2);
INSERT INTO base_de_donnee_etudiant_groupes (etudiant_id, groupe_id)
VALUES 
(1,2);
select * from base_de_donnee_instruction;

-- Insert 1: Groupe 1, Instruction 1, marked as done, no file
INSERT INTO base_de_donnee_instructionstatus (instruction_id, groupe_id, est_termine, fichier_livrable)
VALUES (5, 2, TRUE, NULL);

-- Insert 2: Groupe 2, Instruction 1, not done yet
INSERT INTO base_de_donnee_instructionstatus (instruction_id, groupe_id, est_termine, fichier_livrable)
VALUES (6, 2, FALSE, NULL);

-- Insert 3: Groupe 1, Instruction 2, done with a file
INSERT INTO base_de_donnee_instructionstatus (instruction_id, groupe_id, est_termine, fichier_livrable)
VALUES (7, 2, TRUE, 'livrables/rapport_groupe1.pdf');

-- Insert 4: Groupe 3, Instruction 1, done, no file
INSERT INTO base_de_donnee_instructionstatus (instruction_id, groupe_id, est_termine, fichier_livrable)
VALUES (5, 3, TRUE, NULL);


INSERT INTO base_de_donnee_taches (groupe_id, etudiant_id, description_tache, status, deadline)
VALUES 
(2, 12, 'Rédiger l’introduction du rapport', 'En cours', '2025-04-25'),
(2, 1, 'Créer le diagramme de séquence', 'Terminé', '2025-04-22'),
(2, 10, 'Préparer la présentation PowerPoint', 'En cours', '2025-04-28'),
(2, 1, 'Corriger les fautes dans le document final', 'Terminé', '2025-04-23');

INSERT INTO base_de_donnee_calendrier (etudiant_id, evenement, date_debut, date_fin, status)
VALUES 
(2, 'Début du projet', '2025-04-10', '2025-04-10', 'bleu'),
(3, 'Livrable 1', '2025-04-24', '2025-04-24', 'jaune'),
(10, 'Réunion groupe', '2025-04-20', '2025-04-20', 'rouge'),
(12, 'Deadline finale', '2025-04-30', '2025-04-30', 'vert');

INSERT INTO base_de_donnee_event (title, start_date, end_date, category, etudiant_id)
VALUES 
('Hackathon UPM', '2025-05-03', '2025-05-05', 'compétition', 2),
('Réunion pédagogique', '2025-04-21', NULL, 'meeting', 3),
('Soumission rapport', '2025-04-30', NULL, 'deadline', 12),
('Cours Sécurité Réseaux', '2025-04-22', '2025-04-22', 'calendar', NULL); -- événement global


select * from base_de_donnee_pnotification;