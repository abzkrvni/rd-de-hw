/*
 Завдання на SQL до лекції 03.
 */


/*
1.
Вивести кількість фільмів в кожній категорії.
Результат відсортувати за спаданням.
*/
-- SQL code goes here...

select 
	c."name" as film_category, 
	COUNT(distinct f.film_id) as films_count
from pagila.public.film f 
left join pagila.public.film_category fc on f.film_id =fc.film_id
left join pagila.public.category c on c.category_id = fc.category_id
group by c."name"
order by COUNT(f.film_id) desc 

/*
2.
Вивести 10 акторів, чиї фільми брали на прокат найбільше.
Результат відсортувати за спаданням.
*/
-- SQL code goes here...

select 
	concat(a.first_name, ' ', a.last_name) as actor, 
	COUNT(distinct r.rental_id) as rentals_count
from pagila.public.rental r
left join pagila.public.inventory i on i.inventory_id = r.inventory_id
left join pagila.public.film_actor fa on fa.film_id = i.film_id 
left join pagila.public.actor a on a.actor_id = fa.actor_id
group by fa.actor_id, a.first_name, a.last_name
order by COUNT(distinct r.rental_id) desc
limit 10

/*
3.
Вивести категорія фільмів, на яку було витрачено найбільше грошей
в прокаті
*/
-- SQL code goes here...

select 
	c."name",	
	SUM(p.amount) as rental_revenue -- film might belong to different categories thus rental payment tmight be accounted for in each of specific film categories
from pagila.public.payment p 
left join pagila.public.rental r on r.rental_id = p.rental_id
left join pagila.public.inventory i on i.inventory_id = r.inventory_id
left join pagila.public.film_category fc on fc.film_id = i.film_id 
left join pagila.public.category c on c.category_id = fc.category_id
group by c."name"
order by SUM(p.amount) desc
limit 1

/*
4.
Вивести назви фільмів, яких не має в inventory.
Запит має бути без оператора IN
*/
-- SQL code goes here...

select 
	f.title
from pagila.public.film f 
left join pagila.public.inventory i on i.film_id = f.film_id 
where i.inventory_id is null 

/*
5.
Вивести топ 3 актори, які найбільше зʼявлялись в категорії фільмів “Children”.
*/
-- SQL code goes here...

select 
	a.actor_id,
	concat(a.first_name, ' ', a.last_name) as actor,
	COUNT(fa.film_id) as films_count
from pagila.public.film_actor fa  
inner join pagila.public.actor a on a.actor_id = fa.actor_id
inner join pagila.public.film_category fc on fc.film_id = fa.film_id
inner join pagila.public.category c on c.category_id = fc.category_id
where c."name" = 'Children'
group by a.actor_id, concat(a.first_name, ' ', a.last_name)
order by COUNT(fa.film_id) desc 
limit 3