def get_user_by_email(cur,email):
    cur.execute(
        """
        SELECT * FROM t_user where email = %s
        """,(email,)
    )
    result = cur.fetchone()
    return result 
