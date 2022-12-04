select
    age,
    count(*) as cnt
from
    titanic
group by 1
order by 1