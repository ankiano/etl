select
    color,
    count(id) as product_cnt,
    sum(price) as value_amt
from product
group by 1