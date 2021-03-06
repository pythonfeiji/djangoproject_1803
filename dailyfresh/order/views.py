import datetime
import os
from django.shortcuts import render
from utils.mixin_util import LoginRequiredMixin
from django.shortcuts import render, redirect
from django.core.urlresolvers import reverse
from django.views.generic import View
from django.conf import settings
from goods.models import *
from user.models import *
from order.models import *
from django.http import JsonResponse
from django.db import transaction
from alipay import AliPay


class OrderPlaceView(LoginRequiredMixin, View):
    '''提交订单页面显示'''

    def post(self, request):
        '''提交订单页面显示'''
        # 获取登录的用户
        user = request.user
        # 获取参数sku_ids
        sku_ids = request.POST.getlist('sku_ids')  # [1,26]

        # 校验参数
        if not sku_ids:
            # 跳转到购物车页面
            return redirect(reverse('cart:show'))

        conn = settings.REDIS_CONN
        cart_key = 'cart_%d' % user.id

        skus = []
        # 保存商品的总件数和总价格
        total_count = 0
        total_price = 0
        # 遍历sku_ids获取用户要购买的商品的信息
        for sku_id in sku_ids:
            # 根据商品的id获取商品的信息
            sku = GoodsSKU.objects.get(id=sku_id)
            # 获取用户所要购买的商品的数量
            count = conn.hget(cart_key, sku_id)
            # 计算商品的小计
            amount = sku.price * int(count)
            # 动态给sku增加属性count,保存购买商品的数量
            sku.count = count
            # 动态给sku增加属性amount,保存购买商品的小计
            sku.amount = amount
            # 追加
            skus.append(sku)
            # 累加计算商品的总件数和总价格
            total_count += int(count)
            total_price += amount

        # 运费:实际开发的时候，属于一个子系统
        transit_price = 10  # 写死，后期要通过物流系统传递过来

        # 实付款
        total_pay = total_price + transit_price

        # 获取用户的收件地址
        addrs = Address.objects.filter(user=user)

        # 组织上下文
        sku_ids = ','.join(sku_ids)  # [1,25]->1,25
        context = {
            'skus': skus,
            'total_count': total_count,
            'total_price': total_price,
            'transit_price': transit_price,
            'total_pay': total_pay,
            'addrs': addrs,
            'sku_ids': sku_ids
        }

        # 使用模板
        return render(request, 'place_order.html', context)


# class OrderCommitView(View):
#     '''订单创建'''
#
#     @transaction.atomic
#     def post(self, request):
#         '''订单创建'''
#         # 判断用户是否登录
#         user = request.user
#         if not user.is_authenticated():
#             # 用户未登录
#             return JsonResponse({'res': 0, 'errmsg': '用户未登录'})
#
#         # 接收参数
#         addr_id = request.POST.get('addr_id')
#         pay_method = request.POST.get('pay_method')
#         sku_ids = request.POST.get('sku_ids')  # 1,3
#
#         # 校验参数
#         if not all([addr_id, pay_method, sku_ids]):
#             return JsonResponse({'res': 1, 'errmsg': '参数不完整'})
#
#         # 校验支付方式
#         try:
#             pay_method = int(pay_method)
#         except ValueError:
#             return JsonResponse({'res': 2, 'errmsg': '非法的支付方式'})
#
#         if pay_method not in dict(OrderInfo.PAY_METHOD_CHOICES).keys():
#             return JsonResponse({'res': 2, 'errmsg': '非法的支付方式'})
#
#         # 校验地址
#         try:
#             addr = Address.objects.get(id=addr_id)
#         except Address.DoesNotExist:
#             # 地址不存在
#             return JsonResponse({'res': 3, 'errmsg': '地址非法'})
#
#         # todo: 创建订单核心业务
#
#         # 组织参数
#         # 订单id: 20171122181630+用户id
#
#         order_id = datetime.datetime.today().strftime('%Y%m%d%H%M%S') + str(user.id)
#
#         # 运费
#         transit_price = 10
#
#         # 总数目和总金额
#         total_count = 0
#         total_price = 0
#
#         try:
#
#             #设置事务保存点
#             save_point = transaction.savepoint()
#
#             # todo: 向df_order_info表中添加一条记录
#             order = OrderInfo.objects.create(
#                 order_id=order_id,
#                 user=user,
#                 addr=addr,
#                 pay_method=pay_method,
#                 total_count=total_count,
#                 total_price=total_price,
#                 transit_price=transit_price
#             )
#
#             #模拟异常
#             # num = 1/0
#
#             # todo: 用户的订单中有几个商品，需要向df_order_goods表中加入几条记录
#             conn = settings.REDIS_CONN
#             cart_key = 'cart_%d' % user.id
#
#             sku_ids = sku_ids.split(',')
#             for sku_id in sku_ids:
#
#                 # 获取商品的信息
#                 try:
#                     # sku = GoodsSKU.objects.get(id=sku_id)
#                     #悲观锁的实现
#                     sku = GoodsSKU.objects.select_for_update().get(id=sku_id)
#
#                     print('用户%s成功获取锁...'%user.id)
#                     import time
#                     time.sleep(10)
#
#
#                 except:
#                     #回滚
#                     transaction.savepoint_rollback(save_point)
#                     # 商品不存在
#                     return JsonResponse({'res': 4, 'errmsg': '商品不存在'})
#
#                 # 从redis中获取用户所要购买的商品的数量
#                 count = conn.hget(cart_key, sku_id)
#
#                 # todo: 判断商品的库存
#                 if int(count) > sku.stock:
#                     # 回滚
#                     transaction.savepoint_rollback(save_point)
#                     return JsonResponse({'res': 6, 'errmsg': '商品库存不足'})
#
#                 # todo: 向df_order_goods表中添加一条记录
#                 OrderGoods.objects.create(
#                     order=order,
#                     sku=sku,
#                     count=count,
#                     price=sku.price
#                 )
#
#                 # todo: 更新商品的库存和销量
#                 sku.stock -= int(count)
#                 sku.sales += int(count)
#                 sku.save()
#
#                 # todo: 累加计算订单商品的总数量和总价格
#                 amount = sku.price * int(count)
#                 total_count += int(count)
#                 total_price += amount
#
#             # todo: 更新订单信息表中的商品的总数量和总价格
#             order.total_count = total_count
#             order.total_price = total_price
#             order.save()
#
#             #提交
#             transaction.savepoint_commit(save_point)
#         except Exception as e:
#             # 回滚
#             transaction.savepoint_rollback(save_point)
#             print('1...')
#             return JsonResponse({'res': 7, 'errmsg': '下单失败'})
#
#         # todo: 清除用户购物车中对应的记录
#         conn.hdel(cart_key, sku_ids)
#
#         # 返回应答
#         return JsonResponse({'res': 5, 'message': '创建成功'})


class OrderCommitView(View):
    '''订单创建'''

    @transaction.atomic
    def post(self, request):
        '''订单创建'''
        # 判断用户是否登录
        user = request.user
        if not user.is_authenticated():
            # 用户未登录
            return JsonResponse({'res': 0, 'errmsg': '用户未登录'})

        # 接收参数
        addr_id = request.POST.get('addr_id')
        pay_method = request.POST.get('pay_method')
        sku_ids = request.POST.get('sku_ids')  # 1,3

        # 校验参数
        if not all([addr_id, pay_method, sku_ids]):
            return JsonResponse({'res': 1, 'errmsg': '参数不完整'})

        # 校验支付方式
        try:
            pay_method = int(pay_method)
        except ValueError:
            return JsonResponse({'res': 2, 'errmsg': '非法的支付方式'})

        if pay_method not in dict(OrderInfo.PAY_METHOD_CHOICES).keys():
            return JsonResponse({'res': 2, 'errmsg': '非法的支付方式'})

        # 校验地址
        try:
            addr = Address.objects.get(id=addr_id)
        except Address.DoesNotExist:
            # 地址不存在
            return JsonResponse({'res': 3, 'errmsg': '地址非法'})

        # todo: 创建订单核心业务

        # 组织参数
        # 订单id: 20171122181630+用户id

        order_id = datetime.datetime.today().strftime('%Y%m%d%H%M%S') + str(user.id)

        # 运费
        transit_price = 10

        # 总数目和总金额
        total_count = 0
        total_price = 0

        try:

            # 设置事务保存点
            save_point = transaction.savepoint()

            # todo: 向df_order_info表中添加一条记录
            order = OrderInfo.objects.create(
                order_id=order_id,
                user=user,
                addr=addr,
                pay_method=pay_method,
                total_count=total_count,
                total_price=total_price,
                transit_price=transit_price
            )

            # 模拟异常
            # num = 1/0

            # todo: 用户的订单中有几个商品，需要向df_order_goods表中加入几条记录
            conn = settings.REDIS_CONN
            cart_key = 'cart_%d' % user.id

            sku_ids = sku_ids.split(',')
            for sku_id in sku_ids:
                for i in range(3):
                    # 获取商品的信息
                    try:
                        sku = GoodsSKU.objects.get(id=sku_id)
                    except:
                        # 回滚
                        transaction.savepoint_rollback(save_point)
                        # 商品不存在
                        return JsonResponse({'res': 4, 'errmsg': '商品不存在'})

                    # 从redis中获取用户所要购买的商品的数量
                    count = conn.hget(cart_key, sku_id)

                    # todo: 判断商品的库存
                    if int(count) > sku.stock:
                        # 回滚
                        transaction.savepoint_rollback(save_point)
                        return JsonResponse({'res': 6, 'errmsg': '商品库存不足'})

                    # todo: 更新商品的库存和销量
                    orgin_stock = sku.stock
                    new_stock = orgin_stock - int(count)
                    new_sales = sku.sales + int(count)

                    # print('user:%d...stock:%d' % (user.id, sku.stock))
                    # import time
                    # time.sleep(10)


                    # 返回受影响的行数   update   xxx  where xxxx
                    res = GoodsSKU.objects.filter(id=sku_id, stock=orgin_stock).update(stock=new_stock, sales=new_sales)
                    if res == 0:
                        if i == 2:
                            transaction.savepoint_rollback(save_point)
                            return JsonResponse({'res': 7, 'errmsg': '下单失败,并发'})
                        continue

                    # todo: 向df_order_goods表中添加一条记录
                    OrderGoods.objects.create(
                        order=order,
                        sku=sku,
                        count=count,
                        price=sku.price
                    )

                    # # todo: 更新商品的库存和销量
                    # sku.stock -= int(count)
                    # sku.sales += int(count)
                    # sku.save()

                    # todo: 累加计算订单商品的总数量和总价格
                    amount = sku.price * int(count)
                    total_count += int(count)
                    total_price += amount

                    break

            # todo: 更新订单信息表中的商品的总数量和总价格
            order.total_count = total_count
            order.total_price = total_price
            order.save()

            # 提交
            transaction.savepoint_commit(save_point)
        except Exception as e:
            # 回滚
            transaction.savepoint_rollback(save_point)
            print('1...')
            return JsonResponse({'res': 7, 'errmsg': '下单失败'})

        # todo: 清除用户购物车中对应的记录
        conn.hdel(cart_key, *sku_ids)

        # 返回应答
        return JsonResponse({'res': 5, 'message': '创建成功'})


class OrderPayView(View):
    '''订单支付'''

    def post(self, request):
        # 用户是否登录
        user = request.user
        if not user.is_authenticated():
            return JsonResponse({'res': 0, 'errmsg': '用户未登录'})

        # 接收参数
        order_id = request.POST.get('order_id')

        # 校验参数
        if not order_id:
            return JsonResponse({'res': 1, 'errmsg': '无效的订单id'})

        try:
            print('order_id:%s' % order_id)
            order = OrderInfo.objects.get(order_id=order_id,
                                          user=user,
                                          pay_method=3,
                                          order_status=1)
        except OrderInfo.DoesNotExist:
            return JsonResponse({'res': 2, 'errmsg': '订单错误'})

        # 业务处理:使用python sdk调用支付宝的支付接口

        # 初始化


        app_private_key_string = os.path.join(settings.BASE_DIR, 'order/app_private_key.pem')
        alipay_public_key_string = os.path.join(settings.BASE_DIR, 'order/alipay_public_key.pem')

        alipay = AliPay(
            appid="2016091900544820",
            app_notify_url=None,  # 默认回调url
            app_private_key_path=app_private_key_string,
            alipay_public_key_path=alipay_public_key_string,  # 支付宝的公钥，验证支付宝回传消息使用，不是你自己的公钥,
            sign_type="RSA2",  # RSA 或者 RSA2
            debug=True  # 默认False
        )

        # 调用支付接口
        subject = "天天生鲜订单-%s" % order.order_id
        total_pay = order.total_price + order.transit_price

        # 电脑网站支付，需要跳转到https: // openapi.alipay.com / gateway.do? + order_string
        order_string = alipay.api_alipay_trade_page_pay(
            out_trade_no=order_id,
            total_amount=str(total_pay),
            subject=subject,
            return_url=None,
            notify_url=None  # 可选, 不填则使用默认notify url
        )

        pay_url = 'https://openapi.alipaydev.com/gateway.do?' + order_string
        return JsonResponse({'res': 3, 'pay_url': pay_url})


class CheckPayView(View):
    '''查看订单支付的结果'''

    def post(self, request):
        '''查询支付结果'''
        # 用户是否登录
        user = request.user
        if not user.is_authenticated():
            return JsonResponse({'res': 0, 'errmsg': '用户未登录'})

        # 接收参数
        order_id = request.POST.get('order_id')

        # 校验参数
        if not order_id:
            return JsonResponse({'res': 1, 'errmsg': '无效的订单id'})

        try:
            print('order_id:%s' % order_id)
            order = OrderInfo.objects.get(order_id=order_id,
                                          user=user,
                                          pay_method=3,
                                          order_status=1)
        except OrderInfo.DoesNotExist:
            return JsonResponse({'res': 2, 'errmsg': '订单错误'})

        # 业务处理:使用python sdk调用支付宝的支付接口

        # 初始化


        app_private_key_string = os.path.join(settings.BASE_DIR, 'order/app_private_key.pem')
        alipay_public_key_string = os.path.join(settings.BASE_DIR, 'order/alipay_public_key.pem')

        alipay = AliPay(
            appid="2016091900544820",
            app_notify_url=None,  # 默认回调url
            app_private_key_path=app_private_key_string,
            alipay_public_key_path=alipay_public_key_string,  # 支付宝的公钥，验证支付宝回传消息使用，不是你自己的公钥,
            sign_type="RSA2",  # RSA 或者 RSA2
            debug=True  # 默认False
        )

        # 调用支付宝的交易查询接口
        while True:
            response = alipay.api_alipay_trade_query(order_id)

            code = response.get('code')

            print('code:%s'%code)

            if code == '10000' and response.get('trade_status') == 'TRADE_SUCCESS':
                # 支付成功
                # 获取支付宝交易号
                trade_no = response.get('trade_no')
                # 更新订单状态
                order.trade_no = trade_no
                order.order_status = 4  # 待评价
                order.save()
                # 返回结果
                return JsonResponse({'res': 3, 'message': '支付成功'})
            elif code == '40004' or (code == '10000' and response.get('trade_status') == 'WAIT_BUYER_PAY'):
                # 等待买家付款
                # 业务处理失败，可能一会就会成功
                import time
                print('休眠5秒后，再次查询订单状态...')
                time.sleep(5)
                continue
            else:
                # 支付出错
                return JsonResponse({'res': 4, 'errmsg': '支付失败'})
