-- -------------------------- --
-- Студент: Козлов А. В.      --
-- Группа: 24-ИС		      --
-- Вариант 8. Школьный журнал --
-- -------------------------- --

DROP DATABASE IF EXISTS Variant8_Work;
-- создание базы данных (1-5)
CREATE DATABASE Variant8_Work;
USE Variant8_Work;
-- таблица Students
CREATE TABLE Students (
	id_студента INT PRIMARY KEY AUTO_INCREMENT,
    фамилия VARCHAR(45) NOT NULL,
    имя VARCHAR(45) NOT NULL,
    отчество VARCHAR(45) NOT NULL,
    класс VARCHAR(45) NOT NULL
);

-- таблица Subjects
CREATE TABLE Subjects (
	id_предмета INT PRIMARY KEY AUTO_INCREMENT,
    название VARCHAR(45) NOT NULL
);

-- таблица Teachers
CREATE TABLE Teachers (
	id_учителя INT PRIMARY KEY AUTO_INCREMENT,
    фамилия VARCHAR(45) NOT NULL,
    имя VARCHAR(45) NOT NULL,
    отчество VARCHAR(45) NOT NULL
);

-- таблица TeacherSubjects
CREATE TABLE TeacherSubjects (
	id_связи INT PRIMARY KEY AUTO_INCREMENT,
    id_учителя INT NOT NULL,
    фамилия VARCHAR(45) NOT NULL,
    id_предмета INT NOT NULL,
    название VARCHAR(45) NOT NULL
);

-- таблица Grades
CREATE TABLE Grades (
	id_оценки INT PRIMARY KEY AUTO_INCREMENT,
    id_студента INT NOT NULL,
    id_предмета INT NOT NULL,
	оценка INT NOT NULL,
    дата DATE NOT NULL
);

-- таблица Attendance
CREATE TABLE Attendance (
	id_посещаемости INT PRIMARY KEY AUTO_INCREMENT,
    id_студента INT NOT NULL,
    дата DATE NOT NULL,
    статус VARCHAR(45) NOT NULL
);

-- заполнение данными (6-8)
INSERT INTO students (id_студента, фамилия, имя, отчество, класс)
VALUES (1, 'Алексеев', 'Дмитрий', 'Сергеевич', '10А'),
(2, 'Белова', 'Анастасия', 'Игоревна', '10А'),
(3, 'Виноградов', 'Максим', 'Андреевич', '10Б'),
(4, 'Григорьева', 'София', 'Владимировна', '10Б'),
(5, 'Дмитриев', 'Артем', 'Николаевич', '11А');

INSERT INTO Subjects (id_предмета, название)
VALUES (1, 'математика'),
(2, 'русский'),
(3, 'информатика');

INSERT INTO Teachers (id_учителя, фамилия, имя, отчество)
VALUES (1, 'Смирнов', 'Иван', 'Петрович'),
(2, 'Новиков', 'Алексей', 'Алексей');

-- связь учителей с предметами (9)
SELECT TeacherSubjects.id_связи, TeacherSubjects.id_учителя, TeacherSubjects.id_предмета, TeacherSubjects.фамилия, TeacherSubjects.название
FROM TeacherSubjects
JOIN Teachers ON TeacherSubjects.id_учителя = Teachers.id_учителя
JOIN Subjects ON TeacherSubjects.id_предмета = Subjects.id_предмета;

-- 10 оценок разным ученикам по разным предметам с датами (10)
INSERT INTO Grades (id_оценки, id_студента, id_предмета, оценка, дата)
VALUES (1, 1, 1, 4, '2026-06-01'),
(2, 2, 2, 4, '2026-06-02'),
(3, 3, 3, 5, '2026-06-01'),
(4, 4, 1, 3, '2026-06-04'),
(5, 5, 2, 5, '2026-06-01'),
(6, 1, 3, 4, '2026-06-02'),
(7, 2, 1, 4, '2026-06-02'),
(8, 3, 2, 3, '2026-06-04'),
(9, 4, 3, 3, '2026-06-04'),
(10, 5, 1, 5, '2026-06-01');

-- посещаемость: 8 записей  (11)
INSERT INTO Attendance (id_посещаемости, id_студента, дата, статус)
VALUES (1, 1, '2026-06-01', 'Присутствовал'),
(2, 2, '2026-06-01', 'Присутствовал'),
(3, 3, '2026-06-01', 'Присутствовал'),
(4, 4, '2026-06-01', 'Отсутствовал'),
(5, 5, '2026-06-02', 'Отсутствовал'),
(6, 1, '2026-06-02', 'Отсутствовал'),
(7, 2, '2026-06-02', 'Присутствовал'),
(8, 3, '2026-06-02', 'Отсутствовал');

-- средний балл ученика "Виноградов" (12)
SELECT id_студента, AVG(оценка) AS средний_балл
FROM Grades
WHERE id_студента = 3;

-- все ученики, у которых есть оценка 5 (13)
SELECT *
FROM Grades
WHERE оценка = 5;

-- отсортированный список учеников по среднему баллу (14)
SELECT id_студента, AVG(оценка) AS средний_балл
FROM Grades
GROUP BY id_студента
HAVING AVG(оценка) > 0
ORDER BY средний_балл DESC;

-- предметы и количество оценок по ним (15)
SELECT id_предмета, COUNT(оценка) AS количество_оценок
FROM Grades
GROUP BY id_предмета;

-- предметы, средний балл которых < 4.5 (16)
SELECT id_предмета, AVG(оценка) AS средний_балл
FROM Grades
GROUP BY id_предмета
HAVING AVG(оценка) < 4.5
ORDER BY средний_балл DESC;

-- дни, когда посещаемость была ниже 75% (17)
SELECT дата, COUNT(статус) AS количество_отсутствующих
FROM Attendance
WHERE статус = 'Присутствовал'
GROUP BY дата
HAVING COUNT(статус) < 3;

-- ученики, у которых есть пропуски (18)
SELECT id_студента, COUNT(статус) AS количество_пропусков
FROM Attendance
WHERE статус = 'Отсутствовал'
GROUP BY id_студента
HAVING COUNT(статус) > 0;

-- сгруппированные оценки по дням и их количество (19)
SELECT оценка, дата, COUNT(оценка) AS количество_оценок
FROM Grades
GROUP BY оценка, дата;

-- ученики, которые не получали оценок по информатике (20)
SELECT id_студента
FROM Grades
WHERE id_предмета != 3;

-- увеличенные баллы всех оценок по математике на 1, но не выше 5 (21)
UPDATE Grades
SET оценка = оценка + 1
WHERE id_предмета = 1;

-- удаленные оценки, у которых дата < 2026-06-05 (22)
DELETE FROM Grades WHERE дата < '2026-06-03';

-- добавленный столбец email в Students (23)
ALTER TABLE Students ADD email VARCHAR(45);

-- представление StudentProgress, показывающее ученика, предмет, средний балл (24)
CREATE TABLE StudentProgress (
	id_студента INT PRIMARY KEY AUTO_INCREMENT,
    ученик VARCHAR(45) NOT NULL,
    предмет VARCHAR(45) NOT NULL,
    средний_балл INT NOT NULL
);

-- список предметов для каждого учителя, которые он ведёт, средний балл по каждому предмету, процент посещаемости - отношение присутствий к общему числу занятий (25)
CREATE TABLE Лист (
	id_учителя INT PRIMARY KEY AUTO_INCREMENT,
    фамилия_учителя VARCHAR(45) NOT NULL,
    предмет VARCHAR(45) NOT NULL,
    средний_балл INT NOT NULL,
    процент_посещаемости INT NOT NULL
);