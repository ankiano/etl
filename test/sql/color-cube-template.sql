select
    color,
    count(id) as product_cnt,
    sum(price) as value_amt
from product
where
    id = {unknown_option}
group by 1